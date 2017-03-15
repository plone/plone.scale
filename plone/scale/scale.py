# -*- coding: utf-8 -*-
from cStringIO import StringIO

import PIL.Image
import PIL.ImageFile
import warnings


# Set a larger buffer size. This fixes problems with jpeg decoding.
# See http://mail.python.org/pipermail/image-sig/1999-August/000816.html for
# details.
PIL.ImageFile.MAXBLOCK = 1000000


def scaleImage(image, width=None, height=None, direction='down',
               quality=88, result=None):
    """Scale the given image data to another size and return the result
    as a string or optionally write in to the file-like `result` object.

    The `image` parameter can either be the raw image data (ie a `str`
    instance) or an open file.

    The `quality` parameter can be used to set the quality of the
    resulting image scales.

    The return value is a tuple with the new image, the image format and
    a size-tuple.  Optionally a file-like object can be given as the
    `result` parameter, in which the generated image scale will be stored.

    The `width`, `height`, `direction` parameters will be passed to
    :meth:`scalePILImage`, which performs the actual scaling.

    The generated image is a JPEG image, unless the original is a PNG or GIF
    image. This is needed to make sure alpha channel information is
    not lost, which JPEG does not support.
    """
    if isinstance(image, str):
        image = StringIO(image)
    image = PIL.Image.open(image)

    # When we create a new image during scaling we loose the format
    # information, so remember it here.
    format_ = image.format
    if format_ not in ('PNG', 'GIF'):
        # Always generate JPEG, except if format is PNG or GIF.
        format_ = 'JPEG'
    elif format_ == 'GIF':
        # GIF scaled looks better if we have 8-bit alpha and no palette
        format_ = 'PNG'

    icc_profile = image.info.get('icc_profile')
    image = scalePILImage(image, width, height, direction)

    # convert to simpler mode if possible
    colors = image.getcolors(maxcolors=256)
    if image.mode not in ('P', 'L') and colors:
        if format_ == 'JPEG':
            # check if it's all grey
            if all(rgb[0] == rgb[1] == rgb[2] for c, rgb in colors):
                image = image.convert('L')
        elif format_ == 'PNG':
            image = image.convert('P')

    new_result = False

    if result is None:
        result = StringIO()
        new_result = True

    image.save(
        result,
        format_,
        quality=quality,
        optimize=True,
        progressive=True,
        icc_profile=icc_profile
    )

    if new_result:
        result = result.getvalue()
    else:
        result.seek(0)

    return result, format_, image.size


def _scale_thumbnail(image, width=None, height=None):
    """Scale with method "thumbnail".

    Aspect Ratio is kept. Resulting image has to fit in the given box.
    If target aspect ratio is different, either width or height is smaller
    than the given target width or height. No cropping!
    """
    if width is None and height is None:
        raise ValueError("Either width or height need to be given.")
    if width is None:
        # calculate a width based on a scale:
        size = image.size
        width = float(size[0]) / float(size[1]) * height
    elif height is None:
        size = image.size
        height = float(size[1]) / float(size[0]) * width
    image.thumbnail((width, height), PIL.Image.ANTIALIAS)
    return image


def scalePILImage(image, width=None, height=None, direction='down'):
    """Scale a PIL image to another size.

    This is all about scaling for the display in a web browser.

    Either width or height - or both - must be given.

    Three different scaling options are supported via `direction`:

    `up`
        scaling scales the smallest dimension up to the required size
        and crops the other dimension if needed.

    `down`
        scaling starts by scaling the largest dimension to the required
        size and crops the other dimension if needed.

    `thumbnail`
        scales to the requested dimensions without cropping. Theresulting
        image may have a different size than requested. This option
        requires both width and height to be specified.

        `keep` is accepted as an alternative spelling for this option,
        but its use is deprecated.

    The `image` parameter must be an instance of the `PIL.Image` class.

    The return value the scaled image in the form of another instance of
    `PIL.Image`.
    """
    # convert zero to None, same sematics: calculate this scale
    if width == 0:
        width = None
    if height == 0:
        height = None
    if width is None and height is None:
        raise ValueError("Either width or height need to be given")

    if direction == "keep":
        warnings.warn(
            'direction="keep" is deprecated, use "thumbnail" instead',
            DeprecationWarning
        )
        direction = "thumbnail"

    if image.mode == "1":
        # Convert black&white to grayscale
        image = image.convert("L")
    elif image.mode == "P":
        # If palette is grayscale, convert to gray+alpha
        # Else convert palette based images to 3x8bit+alpha
        palette = image.getpalette()
        if palette[0::3] == palette[1::3] == palette[2::3]:
            image = image.convert("LA")
        else:
            image = image.convert("RGBA")
    elif image.mode == "CMYK":
        # Convert CMYK to RGB, allowing for web previews of print images
        image = image.convert("RGB")

    # for thumbnail we're done:
    if direction == 'thumbnail':
        return _scale_thumbnail(image, width, height)

    # now for up and down scaling
    # Determine scale factor needed to get the right height
    factor_height = factor_width = None
    if height is not None:
        factor_height = (float(height) / float(image.size[1]))
    if width is not None:
        factor_width = (float(width) / float(image.size[0]))

    if (factor_height >= 1 or factor_width >= 1) and direction == 'down':
        # However, for this example scaling calculations after this block fail
        # badly:
        # - image with size (129, 100)
        # - target boxed size (400, 99999)
        # - we get a factor_width, factor_height: (3.10077519379845, 249.9975)
        #   and new_width, new_height of (128999, 99999)
        #   that brings down PIL by eating all the available memory.
        return image

    if factor_height == factor_width:
        # The original already has the right aspect ratio, so we only need
        # to scale.
        if direction == 'down':
            image.thumbnail((width, height), PIL.Image.ANTIALIAS)
            return image
        return image.resize((width, height), PIL.Image.ANTIALIAS)

    # figure out which axis to scale. One of the factors can still be None!
    # calculate for 'down'
    use_height = factor_width > factor_height
    if direction == 'up':  # for 'up': invert
        use_height = not use_height

    new_width = width
    new_height = height

    # keep aspect ratio, crop later
    if (height is None or (use_height and width is not None)):
        new_height = int(round(image.size[1] * factor_width))

    if (width is None or (height is not None and not use_height)):
        new_width = int(round(image.size[0] * factor_height))

    image.draft(image.mode, (new_width, new_height))
    image = image.resize((new_width, new_height), PIL.Image.ANTIALIAS)

    # cropping
    if (
        (width is not None and new_width > width) or
        (height is not None and new_height > height)
    ):
        if use_height:
            left = 0
            right = new_width
            top = int((new_height - height) / 2.0)
            bottom = top + height
        else:
            left = int((new_width - width) / 2.0)
            right = left + width
            top = 0
            bottom = new_height
        image = image.crop((left, top, right, bottom))
    return image
