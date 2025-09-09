from io import BytesIO as StringIO
from plone.scale.scale import calculate_scaled_dimensions
from plone.scale.scale import scaleImage
from plone.scale.scale import scalePILImage
from plone.scale.tests import TEST_DATA_LOCATION
from unittest import TestCase

import functools
import os.path
import PIL.Image
import PIL.ImageDraw
import warnings


with open(os.path.join(TEST_DATA_LOCATION, "logo.png"), "rb") as fio:
    PNG = fio.read()
with open(os.path.join(TEST_DATA_LOCATION, "logo.gif"), "rb") as fio:
    GIF = fio.read()
with open(os.path.join(TEST_DATA_LOCATION, "logo.tiff"), "rb") as fio:
    TIFF = fio.read()
with open(os.path.join(TEST_DATA_LOCATION, "cmyk.jpg"), "rb") as fio:
    CMYK = fio.read()
with open(os.path.join(TEST_DATA_LOCATION, "profile.jpg"), "rb") as fio:
    PROFILE = fio.read()
with open(os.path.join(TEST_DATA_LOCATION, "profile.webp"), "rb") as fio:
    PROFILE_WEBP = fio.read()
with open(os.path.join(TEST_DATA_LOCATION, "animated.gif"), "rb") as fio:
    ANIGIF = fio.read()
with open(os.path.join(TEST_DATA_LOCATION, "animated2.gif"), "rb") as fio:
    ANIGIF2 = fio.read()
with open(os.path.join(TEST_DATA_LOCATION, "greyscale_image.png"), "rb") as fio:
    GREYSCALE_IMG = fio.read()


class ScalingTests(TestCase):
    def testNewSizeReturned(self):
        (imagedata, format, size) = scaleImage(PNG, 42, 51, "contain")
        input = StringIO(imagedata)
        image = PIL.Image.open(input)
        self.assertEqual(image.size, size)

    def testScaledImageKeepPNG(self):
        self.assertEqual(scaleImage(PNG, 84, 103, "contain")[1], "PNG")

    def testScaledImageKeepGIFto(self):
        self.assertEqual(scaleImage(GIF, 84, 103, "contain")[1], "PNG")

    def testScaledImageIsJpeg(self):
        self.assertEqual(scaleImage(TIFF, 84, 103, "contain")[1], "JPEG")

    def testScaledAnigifKeepGIF(self):
        self.assertEqual(scaleImage(ANIGIF, 84, 103, "contain")[1], "GIF")

    def testScaledAnigifKeepGIF2(self):
        self.assertEqual(scaleImage(ANIGIF2, 84, 103, "contain")[1], "GIF")

    def testAlphaForcesPNG(self):
        # first image without alpha
        src = PIL.Image.new("RGBA", (256, 256), (255, 255, 255, 255))
        for y in range(0, 256):
            for x in range(0, 256):
                src.putpixel((x, y), (x, y, 0, 255))
        result = StringIO()
        src.save(result, "TIFF")
        self.assertEqual(scaleImage(result, 84, 103, "contain")[1], "JPEG")
        # now with alpha
        src = PIL.Image.new("RGBA", (256, 256), (255, 255, 255, 128))
        result = StringIO()
        for y in range(0, 256):
            for x in range(0, 256):
                src.putpixel((x, y), (x, y, 0, x))
        src.save(result, "TIFF")
        self.assertEqual(scaleImage(result, 84, 103, "contain")[1], "PNG")

    def testScaledCMYKIsRGB(self):
        (imagedata, format, size) = scaleImage(CMYK, 42, 51, "contain")
        input = StringIO(imagedata)
        image = PIL.Image.open(input)
        self.assertEqual(image.mode, "RGB")

    def testScaledPngImageIsPng(self):
        self.assertEqual(scaleImage(PNG, 84, 103, "contain")[1], "PNG")

    def testScaledPreservesProfile(self):
        (imagedata, format, size) = scaleImage(PROFILE, 42, 51, "contain")
        input = StringIO(imagedata)
        image = PIL.Image.open(input)
        self.assertIsNotNone(image.info.get("icc_profile"))

    def testScaleWithFewColorsStaysColored(self):
        (imagedata, format, size) = scaleImage(PROFILE, 16, None, "contain")
        image = PIL.Image.open(StringIO(imagedata))
        self.assertEqual(max(image.size), 16)
        self.assertEqual(image.mode, "RGB")
        self.assertEqual(image.format, "JPEG")

    def testScaledWebp(self):
        (imagedata, format, size) = scaleImage(PROFILE_WEBP, 120, 120)
        self.assertEqual(format, "WEBP")
        self.assertEqual(size, (120, 120))
        self.assertTrue(len(imagedata) < len(PROFILE_WEBP))
        input = StringIO(imagedata)
        image = PIL.Image.open(input)
        self.assertIsNotNone(image.info.get("icc_profile"))

    def testAutomaticGreyscale(self):
        src = PIL.Image.new("RGB", (256, 256), (255, 255, 255))
        draw = PIL.ImageDraw.Draw(src)
        for i in range(0, 256):
            draw.line(((0, i), (256, i)), fill=(i, i, i))
        result = StringIO()
        src.save(result, "JPEG")
        (imagedata, format, size) = scaleImage(result, 200, None, "contain")
        image = PIL.Image.open(StringIO(imagedata))
        self.assertEqual(max(image.size), 200)
        self.assertEqual(image.mode, "L")
        self.assertEqual(image.format, "JPEG")

    def testMaintainLAModeForPalettePNG(self):
        """Test that a palette (P) mode PNG with transparency maintains alpha channel."""
        # Open the image using the project's pattern

        # Verify the original image is in P mode
        original_image = PIL.Image.open(StringIO(GREYSCALE_IMG))
        self.assertEqual(original_image.mode, "P", "Test image should start in P mode")

        # Scale the image
        scaled_data, format_, size = scaleImage(GREYSCALE_IMG, 100, None, "contain")

        # Open the scaled result and check properties
        scaled_image = PIL.Image.open(StringIO(scaled_data))

        # Check the image is not all black (not losing transparency)
        histogram = scaled_image.histogram()
        self.assertFalse(
            histogram[0] > sum(histogram[1:]),
            "Scaled image appears to be mostly black, which indicates alpha information was lost",
        )

        # Verify transparency is maintained in some form
        self.assertEqual(
            scaled_image.mode,
            "LA",
            f"Expected image to maintain transparency with LA mode, but mode is {scaled_image.mode}",
        )

        # Check size constraints were followed
        self.assertLessEqual(max(scaled_image.size), 100)

        # Check format maintained
        self.assertEqual(scaled_image.format, "PNG")

    def testAutomaticPalette(self):
        # get a JPEG with more than 256 colors
        jpeg = PIL.Image.open(StringIO(PROFILE))
        self.assertEqual(jpeg.mode, "RGB")
        self.assertEqual(jpeg.format, "JPEG")
        self.assertIsNone(jpeg.getcolors(maxcolors=256))
        # convert to PNG
        dst = StringIO()
        jpeg.save(dst, "PNG")
        dst.seek(0)
        png = PIL.Image.open(dst)
        self.assertEqual(png.mode, "RGB")
        self.assertEqual(png.format, "PNG")
        self.assertIsNone(png.getcolors(maxcolors=256))
        # scale it to a size where we get less than 256 colors
        (imagedata, format, size) = scaleImage(dst.getvalue(), 24, None, "contain")
        image = PIL.Image.open(StringIO(imagedata))
        # we should now have an image in palette mode
        self.assertEqual(image.mode, "P")
        self.assertEqual(image.format, "PNG")

    def testSameSizeDownScale(self):
        self.assertEqual(scaleImage(PNG, 84, 103, "contain")[2], (84, 103))

    def testHalfSizeDownScale(self):
        self.assertEqual(scaleImage(PNG, 42, 51, "contain")[2], (42, 51))

    def testScaleWithCropDownScale(self):
        self.assertEqual(scaleImage(PNG, 20, 51, "contain")[2], (20, 51))

    def testNoStretchingDownScale(self):
        self.assertEqual(scaleImage(PNG, 200, 103, "contain")[2], (200, 103))

    def testHugeScale(self):
        # The image will be cropped, but not scaled.
        # If such a ridiculous height is given, we only look at the width.
        self.assertEqual(scaleImage(PNG, 400, 99999, "contain")[2], (400, 400))

    def testZeroHeightScale(self):
        # In this case we only look at the width.
        self.assertEqual(scaleImage(PNG, 400, 0, "contain")[2], (400, 400))

    def testNegativeHeightScale(self):
        # In this case we only look at the width.
        self.assertEqual(scaleImage(PNG, 400, -1, "contain")[2], (400, 400))

    def testCropPreWideScaleUnspecifiedHeight(self):
        image = scaleImage(PNG, 400, None, "contain")
        self.assertEqual(image[2], (400, 400))

    def testCropPreWideScale(self):
        image = scaleImage(PNG, 400, 100, "contain")
        self.assertEqual(image[2], (400, 100))

    def testCropPreTallScaleUnspecifiedWidth(self):
        image = scaleImage(PNG, None, 400, "contain")
        self.assertEqual(image[2], (326, 400))

    def testCropPreTallScale(self):
        image = scaleImage(PNG, 100, 400, "contain")
        self.assertEqual(image[2], (100, 400))

    def testRestrictWidthOnlyDownScaleNone(self):
        self.assertEqual(scaleImage(PNG, 42, None, "contain")[2], (42, 42))

    def testRestrictWidthOnlyDownScaleZero(self):
        self.assertEqual(scaleImage(PNG, 42, 0, "contain")[2], (42, 42))

    def testRestrictHeightOnlyDownScaleNone(self):
        self.assertEqual(scaleImage(PNG, None, 51, "contain")[2], (42, 51))

    def testRestrictHeightOnlyDownScaleZero(self):
        self.assertEqual(scaleImage(PNG, 0, 51, "contain")[2], (42, 51))

    def testSameSizeUpScale(self):
        self.assertEqual(scaleImage(PNG, 84, 103, "cover")[2], (84, 103))

    def testDoubleSizeUpScale(self):
        self.assertEqual(scaleImage(PNG, 168, 206, "cover")[2], (168, 206))

    def testHalfSizeUpScale(self):
        self.assertEqual(scaleImage(PNG, 42, 51, "cover")[2], (42, 51))

    def testNoStretchingUpScale(self):
        self.assertEqual(scaleImage(PNG, 200, 103, "cover")[2], (84, 103))

    def testRestrictWidthOnlyUpScaleNone(self):
        self.assertEqual(scaleImage(PNG, 42, None, "cover")[2], (42, 52))

    def testRestrictWidthOnlyUpScaleZero(self):
        self.assertEqual(scaleImage(PNG, 42, 0, "cover")[2], (42, 52))

    def testRestrictHeightOnlyUpScaleNone(self):
        self.assertEqual(scaleImage(PNG, None, 51, "cover")[2], (42, 51))

    def testRestrictHeightOnlyUpScaleZero(self):
        self.assertEqual(scaleImage(PNG, 0, 51, "cover")[2], (42, 51))

    def testNoRestrictionsNone(self):
        self.assertRaises(ValueError, scaleImage, PNG, None, None)

    def testNoRestrictionsZero(self):
        self.assertRaises(ValueError, scaleImage, PNG, 0, 0)

    def testKeepAspectRatio(self):
        self.assertEqual(scaleImage(PNG, 80, 80, "scale")[2], (65, 80))

    def testThumbnailHeightNone(self):
        self.assertEqual(scaleImage(PNG, 42, None, "scale")[2], (42, 51))

    def testThumbnailWidthNone(self):
        self.assertEqual(scaleImage(PNG, None, 51, "scale")[2], (41, 51))

    def testQuality(self):
        img1 = scaleImage(CMYK, 84, 103)[0]
        img2 = scaleImage(CMYK, 84, 103, quality=50)[0]
        img3 = scaleImage(CMYK, 84, 103, quality=20)[0]
        self.assertNotEqual(img1, img2)
        self.assertNotEqual(img1, img3)
        self.assertTrue(len(img1) > len(img2) > len(img3))

    def testResultBuffer(self):
        img1 = scaleImage(PNG, 84, 103)[0]
        result = StringIO()
        img2 = scaleImage(PNG, 84, 103, result=result)[0]
        self.assertEqual(result, img2)  # the return value _is_ the buffer
        self.assertEqual(result.getvalue(), img1)  # but with the same value

    def testAlternativeSpellings(self):
        """Test alternative and deprecated mode spellings and the old
        ``direction`` arguments instead of ``mode``.
        """

        # Test mode contain.  This can do cropping.
        # scale-crop-to-fit
        img = PIL.Image.new("RGB", (20, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 10, 5, direction="scale-crop-to-fit")
        self.assertEqual(img_scaled.size, (10, 5))
        # down
        img = PIL.Image.new("RGB", (20, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 10, 5, direction="down")
        self.assertEqual(img_scaled.size, (10, 5))

        # Test mode cover
        # scale-crop-to-fill
        img = PIL.Image.new("RGB", (20, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 40, 30, direction="scale-crop-to-fill")
        self.assertEqual(img_scaled.size, (30, 30))
        # up
        img = PIL.Image.new("RGB", (20, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 40, 30, direction="up")
        self.assertEqual(img_scaled.size, (30, 30))

        # Test mode scale
        # keep A
        img = PIL.Image.new("RGB", (20, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 20, 10, direction="keep")
        self.assertEqual(img_scaled.size, (10, 10))
        # keep B
        img = PIL.Image.new("RGB", (20, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 40, 80, direction="keep")
        self.assertEqual(img_scaled.size, (20, 20))
        # thumbnail A
        img = PIL.Image.new("RGB", (20, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 20, 10, direction="thumbnail")
        self.assertEqual(img_scaled.size, (10, 10))
        # thumbnail B
        img = PIL.Image.new("RGB", (20, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 40, 80, direction="thumbnail")
        self.assertEqual(img_scaled.size, (20, 20))

    def testModes(self):
        """Test modes to actually behavie like documented."""
        # Mode contain
        # v
        # A
        img = PIL.Image.new("RGB", (20, 40), (0, 0, 0))
        img_scaled = scalePILImage(img, 10, 10, mode="contain")
        self.assertEqual(img_scaled.size, (10, 10))
        # B
        img = PIL.Image.new("RGB", (40, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 10, 10, mode="contain")
        self.assertEqual(img_scaled.size, (10, 10))
        # ^
        # A
        img = PIL.Image.new("RGB", (20, 40), (0, 0, 0))
        img_scaled = scalePILImage(img, 60, 60, mode="contain")
        self.assertEqual(img_scaled.size, (60, 60))
        # B
        img = PIL.Image.new("RGB", (40, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 60, 60, mode="contain")
        self.assertEqual(img_scaled.size, (60, 60))

        # Mode cover
        # v
        # A
        img = PIL.Image.new("RGB", (20, 40), (0, 0, 0))
        img_scaled = scalePILImage(img, 10, 10, mode="cover")
        self.assertEqual(img_scaled.size, (5, 10))
        # B
        img = PIL.Image.new("RGB", (40, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 10, 10, mode="cover")
        self.assertEqual(img_scaled.size, (10, 5))
        # ^
        # A
        img = PIL.Image.new("RGB", (20, 40), (0, 0, 0))
        img_scaled = scalePILImage(img, 60, 60, mode="cover")
        self.assertEqual(img_scaled.size, (30, 60))
        # B
        img = PIL.Image.new("RGB", (40, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 60, 60, mode="cover")
        self.assertEqual(img_scaled.size, (60, 30))

        # Mode scale
        # v
        # A
        img = PIL.Image.new("RGB", (20, 40), (0, 0, 0))
        img_scaled = scalePILImage(img, 10, 10, mode="scale")
        self.assertEqual(img_scaled.size, (5, 10))
        # B
        img = PIL.Image.new("RGB", (40, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 10, 10, mode="scale")
        self.assertEqual(img_scaled.size, (10, 5))
        # ^
        # A
        img = PIL.Image.new("RGB", (20, 40), (0, 0, 0))
        img_scaled = scalePILImage(img, 60, 60, mode="scale")
        self.assertEqual(img_scaled.size, (20, 40))
        # B
        img = PIL.Image.new("RGB", (40, 20), (0, 0, 0))
        img_scaled = scalePILImage(img, 60, 60, mode="scale")
        self.assertEqual(img_scaled.size, (40, 20))

    def testDeprecations(self):
        import plone.scale.scale

        # clear warnings registry, so the test actually sees the warning
        plone.scale.scale.__warningregistry__.clear()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            scaleImage(PNG, 16, 16, direction="keep")
            self.assertEqual(len(w), 1)
            self.assertIs(w[0].category, DeprecationWarning)
            self.assertIn("The 'direction' option is deprecated", str(w[0].message))

    def testDeprecationsAni(self):
        import plone.scale.scale

        # clear warnings registry, so the test actually sees the warning
        plone.scale.scale.__warningregistry__.clear()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            scaleImage(ANIGIF, 16, 16, direction="keep")
            self.assertEqual(len(w), 6)
            for item in w:
                self.assertIs(item.category, DeprecationWarning)
                self.assertIn("The 'direction' option is deprecated", str(item.message))

    def test_calculate_scaled_dimensions_contain(self):
        """Test the calculate_scaled_dimensions function with mode "contain".

        You pass it:

            original_width, original_height, width, height

        Plus an optional mode, by default "scale"`.
        Alternative spellings: `scale-crop-to-fit`, `down`.
        """
        calc = functools.partial(calculate_scaled_dimensions, mode="contain")
        self.assertEqual(calc(1, 1, 1, 1), (1, 1))
        self.assertEqual(calc(10, 10, 1, 1), (1, 1))
        self.assertEqual(calc(1, 1, 10, 10), (10, 10))
        self.assertEqual(calc(10, 20, 10, 10), (10, 10))
        # Try the new preview scale.
        # This is defined as width 400 and a very large height.
        # That does not work at all for cropping.
        self.assertEqual(calc(10, 20, 400, 65536), (400, 400))
        self.assertEqual(calc(600, 300, 400, 65536), (400, 400))
        self.assertEqual(calc(600, 1200, 400, 65536), (400, 400))

    def test_calculate_scaled_dimensions_cover(self):
        """Test calculate_scaled_dimensions function with mode "cover".

        Alternative spellings: `scale-crop-to-fill`, `up`.
        Despite what you may think, this does not crop.
        """
        calc = functools.partial(calculate_scaled_dimensions, mode="cover")
        self.assertEqual(calc(1, 1, 1, 1), (1, 1))
        self.assertEqual(calc(10, 10, 1, 1), (1, 1))
        # Mode "cover" scales up:
        self.assertEqual(calc(1, 1, 10, 10), (10, 10))
        # If any cropping would happen, the next answer would be (10, 10):
        self.assertEqual(calc(10, 20, 10, 10), (5, 10))
        # Try the new preview scale:
        self.assertEqual(calc(10, 20, 400, 65536), (400, 800))
        self.assertEqual(calc(600, 300, 400, 65536), (400, 200))
        self.assertEqual(calc(600, 1200, 400, 65536), (400, 800))

    def test_calculate_scaled_dimensions_scale(self):
        """Test calculate_scaled_dimensions function with mode "scale".

        Alternative spellings: `keep`, `thumbnail`.
        "scale" is the default
        """
        # calc = functools.partial(calculate_scaled_dimensions, mode="scale")
        calc = calculate_scaled_dimensions
        self.assertEqual(calc(1, 1, 1, 1), (1, 1))
        self.assertEqual(calc(10, 10, 1, 1), (1, 1))
        # Mode "scale" only scales down, not up:
        self.assertEqual(calc(1, 1, 10, 10), (1, 1))
        self.assertEqual(calc(10, 20, 10, 10), (5, 10))
        # Try the new preview scale:
        self.assertEqual(calc(10, 20, 400, 65536), (10, 20))
        self.assertEqual(calc(600, 300, 400, 65536), (400, 200))
        self.assertEqual(calc(600, 1200, 400, 65536), (400, 800))

    def testAnimatedGifContainsAllFrames(self):
        image = scaleImage(ANIGIF, 84, 103, "contain")[0]
        with PIL.Image.open(StringIO(image)) as img:
            frames = [frame for frame in PIL.ImageSequence.Iterator(img)]
            self.assertEqual(len(frames), 6)
            for frame in frames:
                self.assertEqual(frame.width, 84)
                self.assertEqual(frame.height, 103)

    def testAnimatedGifContainsAllFrames2(self):
        image = scaleImage(ANIGIF2, 84, 103, "contain")[0]
        with PIL.Image.open(StringIO(image)) as img:
            frames = [frame for frame in PIL.ImageSequence.Iterator(img)]
            self.assertEqual(len(frames), 35)
            for frame in frames:
                self.assertEqual(frame.width, 84)
                self.assertEqual(frame.height, 103)

    def testTargetDimensionsMinimumOnePixel(self):
        """Test that target dimensions are never less than 1 pixel."""
        # Test extremely small scale factors that could result in sub-pixel dimensions
        # Create a very wide image and scale to a tiny width
        img = PIL.Image.new("RGB", (1000, 10), (0, 0, 0))
        img_scaled = scalePILImage(img, 1, 100, mode="scale")
        self.assertGreaterEqual(img_scaled.size[0], 1)  # Width should be at least 1
        self.assertGreaterEqual(img_scaled.size[1], 1)  # Height should be at least 1

        # Create a very tall image and scale to a tiny height
        img = PIL.Image.new("RGB", (10, 1000), (0, 0, 0))
        img_scaled = scalePILImage(img, 100, 1, mode="scale")
        self.assertGreaterEqual(img_scaled.size[0], 1)  # Width should be at least 1
        self.assertGreaterEqual(img_scaled.size[1], 1)  # Height should be at least 1

        # Edge case: try scaling a 1x1 image to less than 1 pixel
        img = PIL.Image.new("RGB", (1, 1), (0, 0, 0))
        img_scaled = scalePILImage(img, 1, 1, mode="scale")
        self.assertGreaterEqual(img_scaled.size[0], 1)  # Width should be at least 1
        self.assertGreaterEqual(img_scaled.size[1], 1)  # Height should be at least 1

    def testCalculateMinimumDimensions(self):
        """Test that _calculate_all_dimensions ensures dimensions are at least 1 pixel."""
        from plone.scale.scale import _calculate_all_dimensions

        # Test with extreme aspect ratios
        dimensions = _calculate_all_dimensions(1000, 10, 1, 100, "scale")
        self.assertGreaterEqual(dimensions.target_width, 1)
        self.assertGreaterEqual(dimensions.target_height, 1)

        dimensions = _calculate_all_dimensions(10, 1000, 100, 1, "scale")
        self.assertGreaterEqual(dimensions.target_width, 1)
        self.assertGreaterEqual(dimensions.target_height, 1)

        # Test with very small dimensions input
        dimensions = _calculate_all_dimensions(1, 1, 1, 1, "scale")
        self.assertGreaterEqual(dimensions.target_width, 1)
        self.assertGreaterEqual(dimensions.target_height, 1)


def test_suite():
    from unittest import defaultTestLoader

    return defaultTestLoader.loadTestsFromName(__name__)
