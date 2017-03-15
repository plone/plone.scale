# -*- coding: utf-8 -*-
from cStringIO import StringIO
from plone.scale.scale import scaleImage
from plone.scale.tests import TEST_DATA_LOCATION
from unittest import TestCase

import os.path
import PIL.Image, PIL.ImageDraw


PNG = open(os.path.join(TEST_DATA_LOCATION, "logo.png")).read()
GIF = open(os.path.join(TEST_DATA_LOCATION, "logo.gif")).read()
TIFF = open(os.path.join(TEST_DATA_LOCATION, "logo.tiff")).read()
CMYK = open(os.path.join(TEST_DATA_LOCATION, "cmyk.jpg")).read()
PROFILE = open(os.path.join(TEST_DATA_LOCATION, "profile.jpg")).read()


class ScalingTests(TestCase):

    def testNewSizeReturned(self):
        (imagedata, format, size) = scaleImage(PNG, 42, 51, "down")
        input = StringIO(imagedata)
        image = PIL.Image.open(input)
        self.assertEqual(image.size, size)

    def testScaledImageKeepPNG(self):
        self.assertEqual(scaleImage(PNG, 84, 103, "down")[1], "PNG")

    def testScaledImageKeepGIFto(self):
        self.assertEqual(scaleImage(GIF, 84, 103, "down")[1], "PNG")

    def testScaledImageIsJpeg(self):
        self.assertEqual(scaleImage(TIFF, 84, 103, "down")[1], "JPEG")

    def testScaledCMYKIsRGB(self):
        (imagedata, format, size) = scaleImage(CMYK, 42, 51, "down")
        input = StringIO(imagedata)
        image = PIL.Image.open(input)
        self.assertEqual(image.mode, "RGB")

    def testScaledPngImageIsPng(self):
        self.assertEqual(scaleImage(PNG, 84, 103, "down")[1], "PNG")

    def testScaledPreservesProfile(self):
        (imagedata, format, size) = scaleImage(PROFILE, 42, 51, "down")
        input = StringIO(imagedata)
        image = PIL.Image.open(input)
        self.assertIsNotNone(image.info.get('icc_profile'))

    def testScaleWithFewColorsStaysColored(self):
        (imagedata, format, size) = scaleImage(PROFILE, 16, None, "down")
        image = PIL.Image.open(StringIO(imagedata))
        self.assertEqual(max(image.size), 16)
        self.assertEqual(image.mode, 'RGB')
        self.assertEqual(image.format, 'JPEG')

    def testAutomaticGreyscale(self):
        src = PIL.Image.new("RGB", (256, 256), (255, 255, 255))
        draw = PIL.ImageDraw.Draw(src)
        for i in range(0, 256):
            draw.line(((0, i), (256, i)), fill=(i, i, i))
        result = StringIO()
        src.save(result, "JPEG")
        (imagedata, format, size) = scaleImage(result, 200, None, "down")
        image = PIL.Image.open(StringIO(imagedata))
        self.assertEqual(max(image.size), 200)
        self.assertEqual(image.mode, 'L')
        self.assertEqual(image.format, 'JPEG')

    def testAutomaticPalette(self):
        # get a JPEG with more than 256 colors
        jpeg = PIL.Image.open(StringIO(PROFILE))
        self.assertEqual(jpeg.mode, 'RGB')
        self.assertEqual(jpeg.format, 'JPEG')
        self.assertIsNone(jpeg.getcolors(maxcolors=256))
        # convert to PNG
        dst = StringIO()
        jpeg.save(dst, "PNG")
        dst.seek(0)
        png = PIL.Image.open(dst)
        self.assertEqual(png.mode, 'RGB')
        self.assertEqual(png.format, 'PNG')
        self.assertIsNone(png.getcolors(maxcolors=256))
        # scale it to a size where we get less than 256 colors
        (imagedata, format, size) = scaleImage(dst.getvalue(), 24, None, "down")
        image = PIL.Image.open(StringIO(imagedata))
        # we should now have an image in palette mode
        self.assertEqual(image.mode, 'P')
        self.assertEqual(image.format, 'PNG')

    def testSameSizeDownScale(self):
        self.assertEqual(scaleImage(PNG, 84, 103, "down")[2], (84, 103))

    def testHalfSizeDownScale(self):
        self.assertEqual(scaleImage(PNG, 42, 51, "down")[2], (42, 51))

    def testScaleWithCropDownScale(self):
        self.assertEqual(scaleImage(PNG, 20, 51, "down")[2], (20, 51))

    def testNoStretchingDownScale(self):
        self.assertEqual(scaleImage(PNG, 200, 103, "down")[2], (84, 103))

    def testRestrictWidthOnlyDownScaleNone(self):
        self.assertEqual(scaleImage(PNG, 42, None, "down")[2], (42, 52))

    def testRestrictWidthOnlyDownScaleZero(self):
        self.assertEqual(scaleImage(PNG, 42, 0, "down")[2], (42, 52))

    def testRestrictHeightOnlyDownScaleNone(self):
        self.assertEqual(scaleImage(PNG, None, 51, "down")[2], (42, 51))

    def testRestrictHeightOnlyDownScaleZero(self):
        self.assertEqual(scaleImage(PNG, 0, 51, "down")[2], (42, 51))

    def testSameSizeUpScale(self):
        self.assertEqual(scaleImage(PNG, 84, 103, "up")[2], (84, 103))

    def testDoubleSizeUpScale(self):
        self.assertEqual(scaleImage(PNG, 168, 206, "up")[2], (168, 206))

    def testHalfSizeUpScale(self):
        self.assertEqual(scaleImage(PNG, 42, 51, "up")[2], (42, 51))

    def testNoStretchingUpScale(self):
        self.assertEqual(scaleImage(PNG, 200, 103, "up")[2], (84, 103))

    def testRestrictWidthOnlyUpScaleNone(self):
        self.assertEqual(scaleImage(PNG, 42, None, "up")[2], (42, 52))

    def testRestrictWidthOnlyUpScaleZero(self):
        self.assertEqual(scaleImage(PNG, 42, 0, "up")[2], (42, 52))

    def testRestrictHeightOnlyUpScaleNone(self):
        self.assertEqual(scaleImage(PNG, None, 51, "up")[2], (42, 51))

    def testRestrictHeightOnlyUpScaleZero(self):
        self.assertEqual(scaleImage(PNG, 0, 51, "up")[2], (42, 51))

    def testNoRestrictionsNone(self):
        self.assertRaises(ValueError, scaleImage, PNG, None, None)

    def testNoRestrictionsZero(self):
        self.assertRaises(ValueError, scaleImage, PNG, 0, 0)

    def testKeepAspectRatio(self):
        self.assertEqual(scaleImage(PNG, 80, 80, "thumbnail")[2], (65, 80))

    def testKeepAspectRatioBBB(self):
        self.assertEqual(scaleImage(PNG, 80, 80, "keep")[2], (65, 80))

    def testThumbnailHeightNone(self):
        self.assertEqual(scaleImage(PNG, 42, None, "thumbnail")[2], (42, 51))

    def testThumbnailWidthNone(self):
        self.assertEqual(scaleImage(PNG, None, 51, "thumbnail")[2], (41, 51))

    def testQuality(self):
        img1 = scaleImage(CMYK, 84, 103)[0]
        img2 = scaleImage(CMYK, 84, 103, quality=50)[0]
        img3 = scaleImage(CMYK, 84, 103, quality=20)[0]
        self.assertNotEqual(img1, img2)
        self.assertNotEqual(img1, img3)
        self.failUnless(len(img1) > len(img2) > len(img3))

    def testResultBuffer(self):
        img1 = scaleImage(PNG, 84, 103)[0]
        result = StringIO()
        img2 = scaleImage(PNG, 84, 103, result=result)[0]
        self.assertEqual(result, img2)      # the return value _is_ the buffer
        self.assertEqual(result.getvalue(), img1)   # but with the same value


def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)
