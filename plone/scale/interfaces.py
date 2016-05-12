# -*- coding: utf-8 -*-s
from zope.interface import Interface


class IScaledImageQuality(Interface):
    """Marker interface for utility query.

    This can be used by plone.app.imaging to define a property "scaled image
    quality" in the site's image handling settings.

    The property can then be used in plone.namedfile as well as in
    Products.Archetypes and Products.ATContentTypes (the latter two currently
    by a patch in plone.app.imaging.monkey).
    """


class IImageScaleFactory(Interface):
    """Creates a scale
    """

    def _call__(
        fieldname=None,
        direction='thumbnail',
        height=None,
        width=None,
        scale=None,
        **parameters
    ):
        """Interface defining an actual scaling operation.

        Arguments are:

        ``context``
            some object with images on

        ``fieldname``
            name of the field to scale

        ``direction``
            is same as PIL direction on scale

        ``width`` and ``height``
            target size

        ``scale``
            name of the current scale, if there is one. Can be used to retrieve
             additional information such as cropping boxes.

        ``**parameters``
            is a dict with optional additional expected keyword arguments

        Expected to return a triple of ``value, format, dimensions``
        or ``None`` on failure.

        ``value``
            is expected to be an storeable value

        ``format``
            is the minor part of the ``image`` mimetype

        ``dimensions``
            is a tuple (width, height)
        """
