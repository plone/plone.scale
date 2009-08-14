import UserDict
import uuid
from zope.component import adapts
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import implements
from zope.annotation import IAnnotations
from plone.scale.scale import scaleImage

class IImageScale(Interface):
    """A scaled image. This is a very simple wrapper around an image scale
    which gives access to its metadata.

    The `id` attribute is usually only guaranteed to be unique within the
    context of a specific original image. For certain storage implementations
    it may be globally unique as well.
    """

    id = Attribute("An identifier uniquely identifying this scale")
    width = Attribute("The pixel width of the image.")
    height = Attribute("The pixel height of the image.")
    url = Attribute("Absolute URL for this image.")
    mimetype = Attribute("The MIME-type of the image.")
    size = Attribute("The size of the image data in bytes.")



class IImageData(Interface):
    """Simple adapater to extract image data from a field. This is needed
    to handle different field types such as :class:`zope.app.file.image.Image`
    and :class:`Products.Archetypes.Fields.ImageField`.
    """
    data = Attribute("The raw image data")



class IImageScaleStorage(Interface):
    """This is an adapter for an image which can store, retrieve and generate
    image scales. It provides a dictionary interface to existing image scales
    using the scale id as key. To find or create a scale based on its scaling
    parameters use the :meth:`scale` method.
    """

    def __init__(image):
        """Adapter constructor."""


    def scale(width=None, height=None, direction=None, create=True):
        """Find a scale based on its parameters. The parameters can be anything
        supported by :meth:`scaleImage`. If an existing scale is found it is
        returned in an :class:`IImageScale` wrapper. If the scale does not exists
        it will be created, unless `create` is `False` in which case `None`
        will be returned instead.
        """

    def __getitem__(self, key):
        """Find a scale based on its id. Returns an object implementing the
        :meth:`IImageScale` interface."""


class ImageScale(object):
    implements(IImageScale)


class AnnotationStorage(UserDict.DictMixin):
    """:class:`IImageScaleStorage` implementation using annotations. Image data
    is stored as an annotation on the object container the image. This is
    needed since not all images are themselves annotatable.

    This is a base class for adapters. Derived classes need to implement
    a constructor which puts the field name in `self.fieldname` and sets 
    `self.annotations` to the appropriate annotation of the content object
    and the :meth:`_getField` and :meth:`_url` methods.

    Information on all existing image scales and their parameters is maintained
    in an annotation with key `plone.scale.<field>`. This annotation has a
    list of tuples. Each tuple describes an image scale and has three components:
    the scale id, a dictionary with scaling parameters and a dictionary which
    describes the scaled image. This last dictionary has the following keys:

    * dimensions: A (width, height) tuple with the image dimensions.
    * mimetype: the MIME type of the image
    * size: size of the image data in bytes

    The image data of the scaled images is stored in an annotation with
    `plone.scale.<field>.<id>` as key.
    """
    # Extra implementation note: the list of scales is kept as a list of
    # (id, scaling parameters, scaled image info) tuples. This is not as ideal
    # as a mapping of parameters to id would be (since parameter->id lookup is
    # the most common operation), but dicts are not hashable making this
    # impossible.

    implements(IImageScaleStorage)

    def __init__(self, context):
        self.context=context
        self.annotations=IAnnotations(context)


    def __repr__(self):
        return "<%s context=%s>" % (self.__clas__.__name__, self.context)
    __str__=__repr__

    def _getField(self, fieldname):
        """Return the image field of the current context. Scales are generated
        based on this data. The base implementation assumes images are
        available as attributes.
        """
        return getattr(self.context, fieldname)


    def _url(self, id):
        """Return the absolute URL for a scaled image with a given id. This
        method must be implemented by derived classes."""
        return id


    def _wrapImageData(self, fieldname, data, details):
        """Hook to transform image data into something that can easily be
        returned to the publication logic."""
        return data


    def scale(self, fieldname, width=None, height=None, direction=None, create=True):
        parameters=dict(width=width, height=height, direction=direction)
        index=self.annotations.get("plone.scale.%s" % fieldname, [])
        for (id, info, details) in index:
            if info==parameters:
                return self._get(id, details)

        if not create:
            return None

        image=self._getField(fieldname)
        data=IImageData(image).data
        (data, format, dimensions)=scaleImage(data, **parameters)
        details=dict(dimensions=dimensions,
                     mimetype="image/%s" % format.lower(),
                     size=len(data))
        id=str(uuid.uuid4())
        index.append((id, parameters, details))
        self.annotations[self._AnnotationKey(id)]=\
                (fieldname, self._wrapImageData(fieldname, data, details))

        return self._get(id, details)


    def _AnnotationKey(self, id):
        """Determine the annotation key for an image scale with id `id`."""
        return "plone.scale.%s" % id


    def _get(self, id, details):
        scale=ImageScale()
        scale.id=id
        scale.width=details["dimensions"][0]
        scale.height=details["dimensions"][1]
        scale.mimetype=details["mimetype"]
        scale.size=details["size"]
        scale.url=self._url(id)
        return scale


    def __getitem__(self, key):
        index=self.annotations.get("plone.scale.%s" % self.fieldname, [])
        for (id, info, details) in index:
            if id==key:
                return self._get(id, details)
        else:
            raise KeyError(key)


    def __setitem__(self, id, scale):
        raise RuntimeError("New scales have to be created via scale()")


    def __delitem__(self, id):
        key=self._AnnotationKey(id)
        fieldname=self.annotations[key][0]
        del self.annotations[key]
        index=self.annotations["plone.scale.%s" % fieldname]
        for i in xrange(len(index)):
            if index[i][0]==id:
                del index[i]
                break


    def __iter__(self):
        key="plone.scale.%s" % self.fieldname
        for (id, _) in self.annotations.get(key, []):
            yield id


    def keys(self):
        return list(self.__iter__())


    def has_key(self, id):
        key=self._AnnotationKey(id)
        return self.annotations.has_key(key)
    __contains__ = has_key

