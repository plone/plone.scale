from lxml import etree

import codecs
import io
import logging
import math
import PIL.Image
import PIL.ImageFile
import PIL.ImageSequence
import re
import sys
import typing
import warnings


try:
    # Pillow 9.1.0+
    LANCZOS = PIL.Image.Resampling.LANCZOS
except AttributeError:
    LANCZOS = PIL.Image.ANTIALIAS

logger = logging.getLogger(__name__)

# When height is higher than this we do not limit the height, but only the width.
# Otherwise cropping does not make sense, and in a Pillow you may get an error.
# In a Pillow traceback I saw 65500 as maximum.
# Several Plone scale definitions have 65536 (2**16).
# So pick a number slightly lower for good measure.
# A different idea was to use -1 here, so we support this:
# a height of 0 or less is ignored.
MAX_HEIGHT = 65000

FLOAT_RE = re.compile(r"(?:\d*\.\d+|\d+)")


def none_as_int(the_int):
    """For python 3 compatibility, to make int vs. none comparison possible
    without changing the algorithms below.

    This should mimic python2 behaviour."""
    if the_int is None:
        return -sys.maxsize
    return the_int


# Set a larger buffer size. This fixes problems with jpeg decoding.
# See http://mail.python.org/pipermail/image-sig/1999-August/000816.html for
# details.
PIL.ImageFile.MAXBLOCK = 1000000

# Try to load images even if they're truncated or have a failing CRC.
PIL.ImageFile.LOAD_TRUNCATED_IMAGES = True

MAX_PIXELS = 8192 * 8192


def scaleImage(
    image,
    width=None,
    height=None,
    mode="scale",
    quality=88,
    result=None,
    direction=None,
):
    """Scale the given image data to another size and return the result
    as a string or optionally write in to the file-like `result` object.

    The `image` parameter can either be the raw image data (ie a `str`
    instance) or an open file.

    The `quality` parameter can be used to set the quality of the
    resulting image scales.

    The return value is a tuple with the new image, the image format and
    a size-tuple.  Optionally a file-like object can be given as the
    `result` parameter, in which the generated image scale will be stored.

    The `width`, `height`, `mode` parameters will be passed to
    :meth:`scalePILImage`, which performs the actual scaling.

    The generated image is a JPEG image, unless the original is a WEBP, PNG
    or GIF image. This is needed to make sure alpha channel information is
    not lost, which JPEG does not support.
    """
    if isinstance(image, (bytes, str)):
        image = io.BytesIO(image)

    animated_kwargs = {}
    with PIL.Image.open(image) as img:
        icc_profile = img.info.get("icc_profile")
        # When we create a new image during scaling we loose the format
        # information, so remember it here.
        format_ = img.format
        if format_ == "GIF":
            # Attempt to process multiple frames, to support animated GIFs
            append_images = []
            for frame in PIL.ImageSequence.Iterator(img):
                # We ignore the returned format_ as it won't get optimized
                # in case of a GIF. This ensures that the format remains
                # constant across all frames.
                scaled_frame, _dummy_format_ = scaleSingleFrame(
                    frame,
                    width=width,
                    height=height,
                    mode=mode,
                    format_=format_,
                    quality=quality,
                    direction=direction,
                )
                append_images.append(scaled_frame)

            # The first image is the basis for save
            # All other images than the first will be added as a save parameter
            image = append_images.pop(0)
            if len(append_images) > 0:
                # Saving as a multi page image
                animated_kwargs["save_all"] = True
                animated_kwargs["append_images"] = append_images
            else:
                # GIF scaled looks better if we have 8-bit alpha and no palette,
                # but it only works for single frame, so don't do this for animated GIFs.
                format_ = "PNG"

        else:
            # All other formats only process a single frame
            if format_ not in ("PNG", "GIF", "WEBP"):
                # Always generate JPEG, except if format is WEBP, PNG or GIF.
                format_ = "JPEG"
            image, format_ = scaleSingleFrame(
                img,
                width=width,
                height=height,
                mode=mode,
                format_=format_,
                quality=quality,
                direction=direction,
            )

    new_result = False
    if result is None:
        result = io.BytesIO()
        new_result = True

    image.save(
        result,
        format_,
        quality=quality,
        optimize=True,
        progressive=True,
        icc_profile=icc_profile,
        **animated_kwargs,
    )

    if new_result:
        result = result.getvalue()
    else:
        result.seek(0)

    return result, format_, image.size


def scaleSingleFrame(
    image,
    width,
    height,
    mode,
    format_,
    quality,
    direction,
):
    image = scalePILImage(image, width, height, mode, direction=direction)

    # convert to simpler mode if possible
    colors = image.getcolors(maxcolors=256)
    if image.mode not in ("P", "L", "LA") and colors:
        if format_ == "JPEG":
            # check if it's all grey
            if all(rgb[0] == rgb[1] == rgb[2] for c, rgb in colors):
                image = image.convert("L")
        elif format_ in ("PNG", "GIF"):
            image = image.convert("P")

    if image.mode == "RGBA" and format_ == "JPEG":
        extrema = dict(zip(image.getbands(), image.getextrema()))
        if extrema.get("A") == (255, 255):
            # no alpha used, just change the mode, which causes the alpha band
            # to be dropped on save
            image = image.convert("RGB")
        else:
            # switch to PNG, which supports alpha
            format_ = "PNG"

    return image, format_


def _scale_thumbnail(image, width=None, height=None):
    """Scale with method "thumbnail".

    Aspect Ratio is kept. Resulting image has to fit in the given box.
    If target aspect ratio is different, either width or height is smaller
    than the given target width or height. No cropping!
    """
    dimensions = _calculate_all_dimensions(
        image.size[0], image.size[1], width, height, "scale"
    )

    if (dimensions.target_width * dimensions.target_height) > MAX_PIXELS:
        # The new image would be excessively large and eat up all memory while
        # scaling, so return the potentially pre cropped image
        return image

    image.draft(image.mode, (dimensions.target_width, dimensions.target_height))
    image = image.resize((dimensions.target_width, dimensions.target_height), LANCZOS)
    return image


def get_scale_mode(mode, direction=None):
    if direction is not None:
        warnings.warn(
            "The 'direction' option is deprecated, use 'mode' instead.",
            DeprecationWarning,
        )
        mode = direction

    if mode in ("scale", "keep", "thumbnail", None):
        return "scale"
    if mode in ("contain", "scale-crop-to-fit", "down"):
        return "contain"
    if mode in ("cover", "scale-crop-to-fill", "up"):
        return "cover"

    return mode


class ScaledDimensions:
    def __init__(self, original_width=0, original_height=0):
        self.final_width = self.target_width = original_width
        self.final_height = self.target_height = original_height
        self.factor_width = self.factor_height = 1.0
        self.post_scale_crop = False
        self.pre_scale_crop = False


def _calculate_all_dimensions(
    original_width, original_height, width, height, mode="scale"
):
    """Calculate all dimensions we need for scaling.

    final_width and final_height are the dimensions of the resulting image and
    are always present.

    The other values are required for cropping and scaling.
    """
    if height is not None and (height >= MAX_HEIGHT or height <= 0):
        height = None

    if mode not in ("contain", "cover", "scale"):
        raise ValueError("Unknown scale mode '%s'" % mode)

    dimensions = ScaledDimensions(
        original_width=original_width,
        original_height=original_height,
    )
    if width is None and height is None:
        return dimensions

    if mode == "scale":
        # calculate missing sizes
        if width is None:
            width = float(original_width) / float(original_height) * height
        elif height is None:
            height = float(original_height) / float(original_width) * width

        # keep aspect ratio of original
        target_width = original_width
        target_height = original_height
        if target_width > width:
            target_height = int(max(target_height * width / target_width, 1))
            target_width = int(width) or 1
        if target_height > height:
            target_width = int(max(target_width * height / target_height, 1))
            target_height = int(height) or 1

        dimensions.target_width = target_width
        dimensions.target_height = target_height

        if (target_width * target_height) > MAX_PIXELS:
            # The new image would be excessively large and eat up all memory while
            # scaling, so return the dimensions of the potentially cropped image
            return dimensions

        dimensions.final_width = dimensions.target_width
        dimensions.final_height = dimensions.target_height
        return dimensions

    # now for 'cover' and 'contain' scaling
    if mode == "contain" and height is None:
        # For cropping we need a height.
        height = width

    # Determine scale factors needed
    factor_height = factor_width = None
    if height is not None:
        factor_height = float(height) / float(original_height)
    if width is not None:
        factor_width = float(width) / float(original_width)

    dimensions.factor_width = factor_width
    dimensions.factor_height = factor_height
    dimensions.final_width = width
    dimensions.final_height = height

    if factor_height == factor_width:
        # The original already has the right aspect ratio
        return dimensions

    # figure out which axis to scale. One of the factors can still be None!
    use_height = none_as_int(factor_width) > none_as_int(factor_height)
    if mode == "cover":  # for 'cover': invert
        use_height = not use_height

    # keep aspect ratio
    if height is None or (use_height and width is not None):
        target_width = width
        target_height = int(round(original_height * factor_width))

    if width is None or (height is not None and not use_height):
        target_width = int(round(original_width * factor_height))
        target_height = height

    # determine whether we need to crop before scaling
    pre_scale_crop = (width is not None and target_width > width) or (
        height is not None and target_height > height
    )
    dimensions.pre_scale_crop = pre_scale_crop

    if pre_scale_crop:
        # crop image before scaling to avoid excessive memory use
        if use_height:
            left = 0
            right = original_width
            top = int(math.floor(((target_height - height) / 2.0) / factor_width))
            bottom = int(
                math.ceil((((target_height - height) / 2.0) + height) / factor_width)
            )
            pre_scale_crop_height = bottom - top
            # set new height in case we abort
            dimensions.final_height = pre_scale_crop_height
            # calculate new scale target_height from cropped height
            target_height = int(round(pre_scale_crop_height * factor_width))
        else:
            left = int(math.floor(((target_width - width) / 2.0) / factor_height))
            right = int(
                math.ceil((((target_width - width) / 2.0) + width) / factor_height)
            )
            top = 0
            bottom = original_height
            pre_scale_crop_width = right - left
            # set new width in case we abort
            dimensions.final_width = pre_scale_crop_width
            # calculate new scale target_width from cropped width
            target_width = int(round(pre_scale_crop_width * factor_height))
        dimensions.pre_scale_crop = (left, top, right, bottom)

    dimensions.target_width = target_width
    dimensions.target_height = target_height

    if (target_width * target_height) > MAX_PIXELS:
        # The new image would be excessively large and eat up all memory while
        # scaling, so return the dimensions of the potentially cropped image
        return dimensions

    dimensions.final_width = target_width
    dimensions.final_height = target_height

    # determine whether we have to crop after scaling due to rounding
    post_scale_crop = (width is not None and target_width > width) or (
        height is not None and target_height > height
    )
    dimensions.post_scale_crop = post_scale_crop

    if post_scale_crop:
        if use_height:
            left = 0
            right = target_width
            top = int((target_height - height) / 2.0)
            bottom = top + height
            dimensions.final_height = bottom - top
        else:
            left = int((target_width - width) / 2.0)
            right = left + width
            top = 0
            bottom = target_height
            dimensions.final_width = right - left
        dimensions.post_scale_crop = (left, top, right, bottom)

    return dimensions


def calculate_scaled_dimensions(
    original_width, original_height, width, height, mode="scale"
):
    """Calculate the scaled image dimensions from the originals using the
    same logic as scalePILImage"""
    dimensions = _calculate_all_dimensions(
        original_width, original_height, width, height, mode
    )

    return (dimensions.final_width, dimensions.final_height)


def scalePILImage(image, width=None, height=None, mode="scale", direction=None):
    """Scale a PIL image to another size.

    This is all about scaling for the display in a web browser.

    Either width or height - or both - must be given.

    Three different scaling options are supported via `mode` and correspond to
    the CSS background-size values
    (see https://developer.mozilla.org/en-US/docs/Web/CSS/background-size):

    `contain`
        Alternative spellings: `scale-crop-to-fit`, `down`.
        Starts by scaling the relatively smallest dimension to the required
        size and crops the other dimension if needed.

    `cover`
        Alternative spellings: `scale-crop-to-fill`, `up`.
        Scales the relatively largest dimension up to the required size.
        Despite the alternative spelling, I see no cropping happening.

    `scale`
        Alternative spellings: `keep`, `thumbnail`.
        Scales to the requested dimensions without cropping. The resulting
        image may have a different size than requested. This option
        requires both width and height to be specified.
        Does not scale up.

    The `image` parameter must be an instance of the `PIL.Image` class.

    The return value the scaled image in the form of another instance of
    `PIL.Image`.
    """
    # convert zero to None, same semantics: calculate this scale
    if width == 0:
        width = None
    if height == 0:
        height = None
    if width is None and height is None:
        raise ValueError("Either width or height need to be given")

    mode = get_scale_mode(mode, direction)

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

    # for scale we're done:
    if mode == "scale":
        return _scale_thumbnail(image, width, height)

    dimensions = _calculate_all_dimensions(
        image.size[0], image.size[1], width, height, mode
    )

    if dimensions.factor_height == dimensions.factor_width:
        # The original already has the right aspect ratio, so we only need
        # to scale.
        if mode == "contain":
            image.thumbnail((dimensions.final_width, dimensions.final_height), LANCZOS)
            return image
        return image.resize((dimensions.final_width, dimensions.final_height), LANCZOS)

    if dimensions.pre_scale_crop:
        # crop image before scaling to avoid excessive memory use
        # in case the intermediate result would be very tall or wide
        image = image.crop(dimensions.pre_scale_crop)

    if (dimensions.target_width * dimensions.target_height) > MAX_PIXELS:
        # The new image would be excessively large and eat up all memory while
        # scaling, so return the potentially pre cropped image
        return image

    image.draft(image.mode, (dimensions.target_width, dimensions.target_height))
    image = image.resize((dimensions.target_width, dimensions.target_height), LANCZOS)

    if dimensions.post_scale_crop:
        # crop off remains due to rounding before scaling
        image = image.crop(dimensions.post_scale_crop)

    return image


def _contain_svg_image(root, target_width: int, target_height: int):
    """Scale SVG viewbox, modifies tree in place.

    Starts by scaling the relatively smallest dimension to the required size and crops the other dimension if needed.
    """
    viewbox = root.attrib.get("viewBox", "").split(" ")
    if len(viewbox) != 4:
        return root

    try:
        viewbox = [int(float(x)) for x in viewbox]
    except ValueError:
        return target_width, target_height
    viewbox_width = viewbox[2]
    viewbox_height = viewbox[3]
    if not viewbox_width or not viewbox_height:
        return target_width, target_height

    # if we have a max height set, make it square
    if target_width == 65536:
        target_width = target_height
    elif target_height == 65536:
        target_height = target_width

    target_ratio = target_width / target_height
    view_box_ratio = viewbox_width / viewbox_height
    if target_ratio < view_box_ratio:
        # narrow down the viewbox width to the same ratio as the target
        width = (target_ratio / view_box_ratio) * viewbox_width
        margin = (viewbox_width - width) / 2
        viewbox[0] = round(viewbox[0] + margin)
        viewbox[2] = round(width)
    else:
        # narrow down the viewbox height to the same ratio as the target
        height = (view_box_ratio / target_ratio) * viewbox_height
        margin = (viewbox_height - height) / 2
        viewbox[1] = round(viewbox[1] + margin)
        viewbox[3] = round(height)
    root.attrib["viewBox"] = " ".join([str(x) for x in viewbox])
    return target_width, target_height


def scale_svg_image(
    image: io.BytesIO,
    target_width: typing.Union[None, int],
    target_height: typing.Union[None, int],
    mode: str = "contain",
) -> typing.Tuple[bytes, typing.Tuple[int, int]]:
    """Scale and crop a SVG image to another display size.

    This is all about scaling for the display in a web browser.

    Either width or height - or both - must be given.

    Three different scaling options are supported via `mode` and correspond to
    the CSS background-size values
    (see https://developer.mozilla.org/en-US/docs/Web/CSS/background-size):

    `contain`
        Alternative spellings: `scale-crop-to-fit`, `down`.
        Starts by scaling the relatively smallest dimension to the required
        size and crops the other dimension if needed.

    `cover`
        Alternative spellings: `scale-crop-to-fill`, `up`.
        Scales the relatively largest dimension up to the required size.
        Despite the alternative spelling, I see no cropping happening.

    `scale`
        Alternative spellings: `keep`, `thumbnail`.
        Scales to the requested dimensions without cropping. The resulting
        image may have a different size than requested. This option
        requires both width and height to be specified.
        Does scale up.

    The `image` parameter must be bytes of the SVG, utf-8 encoded.

    The return value the scaled bytes in the form of another instance of
    `PIL.Image`.
    """
    mode = get_scale_mode(mode)

    if isinstance(image, io.StringIO):
        image = codecs.EncodedFile(image, "utf-8")
        warnings.warn(
            "The 'image' is a StringIO, but a BytesIO is needed, autoconvert.",
            DeprecationWarning,
        )
    tree = etree.parse(image)
    root = tree.getroot()
    source_width, source_height = root.attrib.get("width", ""), root.attrib.get(
        "height", ""
    )

    # strip units from width and height
    match = FLOAT_RE.match(source_width)
    if match:
        source_width = match.group(0)
    match = FLOAT_RE.match(source_height)
    if match:
        source_height = match.group(0)

    # to float
    try:
        source_width, source_height = float(source_width), float(source_height)
    except ValueError:
        logger.exception(
            f"Can not convert source dimensions: '{source_width}':'{source_height}'"
        )
        data = image.read()
        if isinstance(data, str):
            return data.encode("utf-8"), (int(target_width), int(target_height))
        return data, (int(target_width), int(target_height))

    source_aspectratio = source_width / source_height
    target_aspectratio = target_width / target_height
    if mode in ["scale", "cover"]:
        # check if new width is larger than the one we get with aspect ratio
        # if we scale on height
        if source_width * target_aspectratio < target_width:
            # keep height, new width
            target_width = target_height * source_aspectratio
        else:
            target_height = target_width / source_aspectratio
    elif mode == "contain":
        target_width, target_height = _contain_svg_image(
            root, target_width, target_height
        )

    root.attrib["width"] = str(int(target_width))
    root.attrib["height"] = str(int(target_height))

    return etree.tostring(tree, encoding="utf-8", xml_declaration=True), (
        int(target_width),
        int(target_height),
    )
