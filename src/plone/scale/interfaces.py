from zope.interface import Interface


class IScaledImageQuality(Interface):
    """Marker interface for utility query.

    This can be used to define a property "scaled image quality" in the site's image
    handling settings.
    """


class IImageScaleFactory(Interface):
    """Creates a scale"""

    def __call__(
        fieldname=None, mode="scale", height=None, width=None, scale=None, **parameters
    ):
        """Interface defining an actual scaling operation.

        Arguments are:

        ``context``
            some object with images on

        ``fieldname``
            name of the field to scale

        ``mode``
            See ``scalePILImage`` for the values that should be accepted.
            This used to be called "direction", which may still be accepted,
            but is deprecated.

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
            is expected to be an storable value

        ``format``
            is the minor part of the ``image`` mimetype

        ``dimensions``
            is a tuple (width, height)
        """

    def get_original_value(fieldname=None):
        """Get the image value.

        In most cases this will be a NamedBlobImage field.
        Should accept an optional fieldname keyword argument.
        If not passed, and there is no self.fieldname set,
        you can try to get it in a different way.
        """
