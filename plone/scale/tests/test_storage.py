from operator import delitem
from operator import itemgetter
from operator import setitem
from plone.testing import zca
from unittest import TestCase
from zope.component import provideAdapter
from zope.interface import implementer

import zope.annotation.attribute
import zope.annotation.interfaces


@implementer(zope.annotation.interfaces.IAttributeAnnotatable)
class _DummyContext:
    pass


class AnnotationStorageTests(TestCase):

    layer = zca.UNIT_TESTING

    def _provide_dummy_scale_adapter(self, result=True):
        from plone.scale.interfaces import IImageScaleFactory
        from zope.component import adapter

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

    def testCleanUpOldItems(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale_old = storage.scale(foo=23, bar=42)
        next_modified = storage.modified() + 1
        storage.modified = lambda: next_modified
        scale_new = storage.scale(foo=23, bar=42)
        self.assertEqual(len(storage), 1)
        self.assertIn(scale_new["uid"], storage)
        self.assertNotIn(scale_old["uid"], storage)

        # When modification time is older than a day, too old scales
        # get purged.
        next_modified = storage.modified() + 24 * 60 * 60 * 1000 + 1
        storage.modified = lambda: next_modified
        scale_newer = storage.scale(foo=23, bar=42)

        self.assertIn(scale_newer["uid"], storage)
        self.assertNotIn(scale_new["uid"], storage)
        self.assertNotIn(scale_old["uid"], storage)
        del storage[scale_newer["uid"]]
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
