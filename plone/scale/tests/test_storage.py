from operator import delitem
from operator import itemgetter
from operator import setitem
from plone.testing import zca
from unittest import TestCase
from zope.component import provideAdapter
from zope.interface import implementer

import zope.annotation.attribute
import zope.annotation.interfaces


_marker = object()


class DummyImage:
    contentType = "image/jpeg"

    def getImageSize(self):
        # width, height
        return 60, 40


@implementer(zope.annotation.interfaces.IAttributeAnnotatable)
class _DummyContext:
    pass


class AnnotationStorageTests(TestCase):
    layer = zca.UNIT_TESTING

    def _provide_dummy_scale_adapter(self, result=_marker):
        from plone.scale.interfaces import IImageScaleFactory
        from zope.component import adapter

        if result is _marker:
            result = DummyImage()
        factory = self.factory

        @implementer(IImageScaleFactory)
        @adapter(_DummyContext)
        class DummyISF:
            def __init__(self, context):
                self.context = context

            def __call__(self, **parameters):
                if result:
                    return factory()
                return None

            def get_original_value(self, fieldname=None):
                return result

        provideAdapter(DummyISF)

    @property
    def storage(self):
        from plone.scale.storage import AnnotationStorage

        provideAdapter(zope.annotation.attribute.AttributeAnnotations)
        storage = AnnotationStorage(_DummyContext())
        storage.modified = lambda: 42
        return storage

    def factory(self, **kw):
        return "some data", "png", (42, 23)

    def testInterface(self):
        from plone.scale.storage import IImageScaleStorage

        storage = self.storage
        self.assertTrue(IImageScaleStorage.providedBy(storage))

    def testScaleForNonExistingScaleWithCreation(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale = storage.scale(foo=23, bar=42)
        self.assertIn("uid", scale)
        self.assertIn("key", scale)
        self.assertEqual(scale["data"], "some data")
        self.assertEqual(scale["width"], 42)

        self.assertEqual(scale["height"], 23)
        self.assertEqual(scale["mimetype"], "image/png")

    def testScaleForNonExistingScaleWithoutCreation(self):
        self._provide_dummy_scale_adapter(result=None)
        storage = self.storage
        scale = storage.scale(foo=23, bar=42)
        self.assertEqual(scale, None)

    def testPreScaleNoWidthAndHeight(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        # It is actually pretty silly to not pass a width and height.
        # We get the original width and height then.
        scale = storage.pre_scale(foo=23, bar=42)
        self.assertIn("uid", scale)
        self.assertIn("key", scale)
        self.assertEqual(scale["data"], None)
        # We get the values from the DummyImage class.
        self.assertEqual(scale["width"], 60)
        self.assertEqual(scale["height"], 40)
        self.assertEqual(scale["mimetype"], "image/jpeg")

    def testPreScaleForNonExistingScale(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale = storage.pre_scale(width=50, height=80)
        self.assertIn("uid", scale)
        self.assertIn("key", scale)
        self.assertEqual(scale["data"], None)
        self.assertEqual(scale["width"], 50)
        # Note: the original image is 60x40.
        # By default we scale without cropping, so you do not get height 80.
        self.assertEqual(scale["height"], 33)
        self.assertEqual(scale["mimetype"], "image/jpeg")
        # Request the same pre scale.
        scale2 = storage.pre_scale(width=50, height=80)
        self.assertEqual(scale2["uid"], scale["uid"])
        self.assertEqual(scale2, scale)
        # This will really generate the scale.
        new_scale = storage.scale(width=50, height=80)
        self.assertEqual(new_scale["uid"], scale["uid"])
        self.assertIn("key", new_scale)
        self.assertEqual(new_scale["data"], "some data")
        # Our dummy adapter is silly and does not do anything with
        # the requested width and height.
        self.assertEqual(new_scale["width"], 42)
        self.assertEqual(new_scale["height"], 23)
        self.assertEqual(new_scale["mimetype"], "image/png")

        # Try cropping as well.
        scale = storage.pre_scale(width=50, height=80, mode="contain")
        self.assertIn("uid", scale)
        self.assertIn("key", scale)
        self.assertEqual(scale["data"], None)
        self.assertEqual(scale["width"], 50)
        self.assertEqual(scale["height"], 80)
        self.assertEqual(scale["mimetype"], "image/jpeg")

    def testPreScaleForNonExistingField(self):
        self._provide_dummy_scale_adapter(None)
        storage = self.storage
        scale = storage.pre_scale(width=50, height=80)
        self.assertIsNone(scale)
        # scale does the same.
        new_scale = storage.scale(width=50, height=80)
        self.assertIsNone(new_scale)

    def test_get_or_generate(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        self.assertIsNone(storage.get("random"))
        self.assertIsNone(storage.get_or_generate("random"))
        scale = storage.pre_scale(width=50, height=80)
        uid = scale["uid"]
        self.assertTrue(uid)
        # 'get' gets the pre generated placeholder info
        placeholder = storage.get(uid)
        self.assertEqual(placeholder["uid"], uid)
        self.assertIsNone(placeholder["data"])
        self.assertEqual(placeholder["width"], 50)
        self.assertEqual(placeholder["height"], 33)
        self.assertEqual(placeholder["mimetype"], "image/jpeg")
        # 'get_or_generate' gets the pre generated placeholder info
        # and generates the scale.
        real = storage.get_or_generate(uid)
        self.assertEqual(real["uid"], uid)
        self.assertEqual(real["data"], "some data")
        self.assertEqual(real["width"], 42)
        self.assertEqual(real["height"], 23)
        self.assertEqual(real["mimetype"], "image/png")

    def test_get_or_generate__stable_uid(self):
        # When get_or_generate actually generates the scale,
        # it should store it with the same uid that was used
        # to find the placeholder info, even if the field
        # has been modified or a modified time is not available
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale = storage.pre_scale(width=50, height=80)
        uid = scale["uid"]
        storage.modified = lambda: 100
        real = storage.get_or_generate(uid)
        self.assertEqual(real["uid"], uid)

    def testScaleForExistingScale(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale1 = storage.scale(foo=23, bar=42)
        scale2 = storage.scale(bar=42, foo=23)
        self.assertIs(scale1, scale2)

    def testScaleForSimilarScales(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale1 = storage.scale(foo=23, bar=42)
        scale2 = storage.scale(bar=42, foo=23, hurz="!")
        self.assertIsNot(scale1, scale2)

    def test_pre_scale_with_and_without_scale_same_uid(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        uid1 = storage.pre_scale(fieldname="image", height=32, width=32)["uid"]
        uid2 = storage.pre_scale(fieldname="image", height=32, width=32, scale="icon")[
            "uid"
        ]
        self.assertEqual(uid1, uid2)

    def test_scale_with_and_without_scale_same_uid(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        uid1 = storage.scale(fieldname="image", height=32, width=32)["uid"]
        uid2 = storage.scale(fieldname="image", height=32, width=32, scale="icon")[
            "uid"
        ]
        self.assertEqual(uid1, uid2)

    def test_scale_without_height_width(self):
        # Ensures that the scale will only be removed from the hash key
        # if we have width and height.
        self._provide_dummy_scale_adapter()
        storage = self.storage
        uid = storage.scale(fieldname="image", scale="icon")["uid"]
        self.assertEqual(uid, "image-icon-b6e2a135d96703b73688a0d91f741a65")

    def testGetItem(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale = storage.scale(foo=23, bar=42)
        uid = scale["uid"]
        scale = storage[uid]
        self.assertIn("uid", scale)
        self.assertIn("key", scale)
        self.assertEqual(scale["data"], "some data")
        self.assertEqual(scale["width"], 42)
        self.assertEqual(scale["height"], 23)
        self.assertEqual(scale["mimetype"], "image/png")

    def testGetUnknownItem(self):
        storage = self.storage
        self.assertRaises(KeyError, itemgetter("foo"), storage)

    def testSetItemNotAllowed(self):
        storage = self.storage
        self.assertRaises(RuntimeError, setitem, storage, "key", None)

    def testIterateWithoutAnnotations(self):
        storage = self.storage
        self.assertEqual(list(storage), [])

    def testIterate(self):
        storage = self.storage
        storage.storage.update(dict(one=None, two=None))
        generator = iter(storage)
        self.assertEqual(set(generator), {"one", "two"})

    def testKeys(self):
        storage = self.storage
        storage.storage.update(dict(one=None, two=None))
        self.assertEqual(set(storage.keys()), {"one", "two"})

    def testNegativeHasKey(self):
        storage = self.storage
        self.assertEqual("one" in storage, False)

    def testPositiveHasKey(self):
        storage = self.storage
        storage.storage.update(dict(one=None))
        self.assertEqual("one" in storage, True)

    def testDeleteNonExistingItem(self):
        storage = self.storage
        # This used to raise a KeyError, but sometimes the underlying storage
        # can get inconsistent, so it is nicer to accept it.
        # See https://github.com/plone/plone.scale/issues/15
        delitem(storage, "foo")

    def testDeleteRemovesItemAndIndex(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale = storage.scale(foo=23, bar=42)
        self.assertEqual(len(storage), 1)
        del storage[scale["uid"]]
        self.assertEqual(len(storage), 0)

    def test_modified_since(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        self.assertEqual(storage.modified(), 42)

        self.assertTrue(storage._modified_since(41))
        self.assertFalse(storage._modified_since(42))
        self.assertFalse(storage._modified_since(43))

        self.assertFalse(storage._modified_since(41, offset=1))
        self.assertTrue(storage._modified_since(40, offset=1))
        self.assertFalse(storage._modified_since(32, offset=10))
        self.assertTrue(storage._modified_since(32, offset=9))

    def testCleanUpOldItemsForSameParameters(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        orig_modified = storage.modified()
        storage.pre_scale(foo=23, bar=42)
        self.assertEqual(len(storage), 1)
        scale_old = storage.scale(foo=23, bar=42)
        self.assertEqual(len(storage), 1)
        storage.pre_scale(foo=23, bar=42)
        scale_old2 = storage.scale(foo=23, bar=42)
        self.assertEqual(len(storage), 1)
        self.assertEqual(scale_old, scale_old2)
        self.assertIn(scale_old["uid"], storage)
        next_modified = orig_modified + 10
        storage.modified = lambda: next_modified
        scale_new = storage.scale(foo=23, bar=42)
        self.assertEqual(len(storage), 2)
        self.assertIn(scale_new["uid"], storage)
        self.assertIn(scale_old["uid"], storage)
        next_modified = orig_modified + 24 * 60 * 60 * 1000 + 1
        storage.modified = lambda: next_modified
        scale_newer = storage.scale(foo=23, bar=42)
        self.assertIn(scale_newer["uid"], storage)
        self.assertIn(scale_new["uid"], storage)
        self.assertNotIn(scale_old["uid"], storage)
        del storage[scale_newer["uid"]]
        del storage[scale_new["uid"]]
        self.assertEqual(len(storage), 0)

    def testCleanUpOldItemsForDifferentParameters(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale_old = storage.scale(foo=23, bar=42)
        orig_modified = storage.modified()
        next_modified = orig_modified + 60000
        storage.modified = lambda: next_modified
        scale_new = storage.scale(foo=23, bar=50)
        self.assertEqual(len(storage), 2)
        self.assertIn(scale_new["uid"], storage)
        self.assertIn(scale_old["uid"], storage)

        # When modification time is older than a day, too old scales
        # get purged.
        next_modified = orig_modified + 24 * 60 * 60 * 1000 + 1
        storage.modified = lambda: next_modified
        scale_newer = storage.scale(foo=23, bar=70)

        self.assertIn(scale_newer["uid"], storage)
        self.assertIn(scale_new["uid"], storage)
        self.assertNotIn(scale_old["uid"], storage)

        next_modified = orig_modified + 24 * 60 * 60 * 1000 * 3
        storage.modified = lambda: next_modified
        scale_even_newer = storage.scale(foo=23, bar=42)
        self.assertIn(scale_even_newer["uid"], storage)
        self.assertNotIn(scale_newer["uid"], storage)
        self.assertNotIn(scale_new["uid"], storage)
        self.assertNotIn(scale_old["uid"], storage)
        del storage[scale_even_newer["uid"]]
        self.assertEqual(len(storage), 0)

    def testCleanUpOldItemsForDifferentFieldname(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale_image = storage.scale(fieldname="image", bar=42)
        next_modified = storage.modified() + 60000
        storage.modified = lambda: next_modified
        scale_leadimage_old = storage.scale(fieldname="leadimage", bar=50)
        self.assertEqual(len(storage), 2)
        self.assertIn(scale_leadimage_old["uid"], storage)
        self.assertIn(scale_image["uid"], storage)

        # When modification time is older than a day, too old scales
        # get purged.  But only for the current fieldname.
        next_modified = storage.modified() + 24 * 60 * 60 * 1000 + 1
        storage.modified = lambda: next_modified
        scale_leadimage_new = storage.scale(fieldname="leadimage", bar=70)

        self.assertIn(scale_leadimage_new["uid"], storage)
        self.assertNotIn(scale_leadimage_old["uid"], storage)
        self.assertIn(scale_image["uid"], storage)

        # If we manually call cleanup without a fieldname,
        # all items are checked.
        storage._cleanup()
        self.assertIn(scale_leadimage_new["uid"], storage)
        self.assertNotIn(scale_image["uid"], storage)
        del storage[scale_leadimage_new["uid"]]
        self.assertEqual(len(storage), 0)

    def testClear(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        storage.scale(foo=23, bar=42)
        self.assertEqual(len(storage), 1)
        storage.clear()
        self.assertEqual(len(storage), 0)


def test_suite():
    from unittest import defaultTestLoader

    return defaultTestLoader.loadTestsFromName(__name__)
