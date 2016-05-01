# -*- coding: utf-8 -*-
from operator import delitem
from operator import itemgetter
from operator import setitem
from plone.testing import zca
from unittest import TestCase


class _DummyContext(object):
    pass


class AnnotationStorageTests(TestCase):

    layer = zca.UNIT_TESTING

    def _provide_dummy_scale_adapter(self, result=True):
        from zope.component import adapter
        from zope.component import provideAdapter
        from zope.interface import implementer
        from plone.scale.interfaces import IImageScaleFactory

        factory = self.factory

        @implementer(IImageScaleFactory)
        @adapter(_DummyContext)
        class DummyISF(object):

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
        storage = AnnotationStorage(_DummyContext())
        storage.modified = lambda: 42
        storage.storage = {}
        return storage

    def factory(self, **kw):
        return 'some data', 'png', (42, 23)

    def testInterface(self):
        from plone.scale.storage import IImageScaleStorage
        storage = self.storage
        self.failUnless(IImageScaleStorage.providedBy(storage))

    def testScaleForNonExistingScaleWithCreationBBB(self):
        storage = self.storage
        scale = storage.scale(factory=self.factory, foo=23, bar=42)
        self.failUnless('uid' in scale)
        self.failUnless('key' in scale)
        self.assertEqual(scale['data'], 'some data')
        self.assertEqual(scale['width'], 42)
        self.assertEqual(scale['height'], 23)
        self.assertEqual(scale['mimetype'], 'image/png')

    def testScaleForNonExistingScaleWithCreation(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale = storage.scale(foo=23, bar=42)
        self.failUnless('uid' in scale)
        self.failUnless('key' in scale)
        self.assertEqual(scale['data'], 'some data')
        self.assertEqual(scale['width'], 42)

        self.assertEqual(scale['height'], 23)
        self.assertEqual(scale['mimetype'], 'image/png')

    def testScaleForNonExistingScaleWithoutCreationBBB(self):
        storage = self.storage
        scale = storage.scale(foo=23, bar=42)
        self.assertEqual(scale, None)

    def testScaleForNonExistingScaleWithoutCreation(self):
        self._provide_dummy_scale_adapter(result=None)
        storage = self.storage
        scale = storage.scale(foo=23, bar=42)
        self.assertEqual(scale, None)

    def testScaleForExistingScaleBBB(self):
        storage = self.storage
        scale1 = storage.scale(factory=self.factory, foo=23, bar=42)
        scale2 = storage.scale(factory=self.factory, bar=42, foo=23)
        self.failUnless(scale1 is scale2)

    def testScaleForExistingScale(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale1 = storage.scale(foo=23, bar=42)
        scale2 = storage.scale(bar=42, foo=23)
        self.failUnless(scale1 is scale2)

    def testScaleForSimilarScalesBBB(self):
        storage = self.storage
        scale1 = storage.scale(factory=self.factory, foo=23, bar=42)
        scale2 = storage.scale(factory=self.factory, bar=42, foo=23, hurz='!')
        self.failIf(scale1 is scale2)

    def testScaleForSimilarScales(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale1 = storage.scale(foo=23, bar=42)
        scale2 = storage.scale(bar=42, foo=23, hurz='!')
        self.failIf(scale1 is scale2)

    def testGetItemBBB(self):
        storage = self.storage
        scale = storage.scale(factory=self.factory, foo=23, bar=42)
        uid = scale['uid']
        scale = storage[uid]
        self.failUnless('uid' in scale)
        self.failUnless('key' in scale)
        self.assertEqual(scale['data'], 'some data')
        self.assertEqual(scale['width'], 42)
        self.assertEqual(scale['height'], 23)
        self.assertEqual(scale['mimetype'], 'image/png')

    def testGetItem(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale = storage.scale(foo=23, bar=42)
        uid = scale['uid']
        scale = storage[uid]
        self.failUnless('uid' in scale)
        self.failUnless('key' in scale)
        self.assertEqual(scale['data'], 'some data')
        self.assertEqual(scale['width'], 42)
        self.assertEqual(scale['height'], 23)
        self.assertEqual(scale['mimetype'], 'image/png')

    def testGetUnknownItem(self):
        storage = self.storage
        self.assertRaises(KeyError, itemgetter('foo'), storage)

    def testSetItemNotAllowed(self):
        storage = self.storage
        self.assertRaises(RuntimeError, setitem, storage, 'key', None)

    def testIterateWithoutAnnotations(self):
        storage = self.storage
        self.assertEqual(list(storage), [])

    def testIterate(self):
        storage = self.storage
        storage.storage.update(one=None, two=None)
        generator = iter(storage)
        self.assertEqual(set(generator), set(['one', 'two']))

    def testKeys(self):
        storage = self.storage
        storage.storage.update(one=None, two=None)
        self.failUnless(isinstance(storage.keys(), list))
        self.assertEqual(set(storage.keys()), set(['one', 'two']))

    def testNegativeHasKey(self):
        storage = self.storage
        self.assertEqual('one' in storage, False)

    def testPositiveHasKey(self):
        storage = self.storage
        storage.storage.update(one=None)
        self.assertEqual('one' in storage, True)

    def testDeleteNonExistingItem(self):
        storage = self.storage
        self.assertRaises(KeyError, delitem, storage, 'foo')

    def testDeleteRemovesItemAndIndexBBB(self):
        storage = self.storage
        scale = storage.scale(factory=self.factory, foo=23, bar=42)
        self.assertEqual(len(storage), 1)
        del storage[scale['uid']]
        self.assertEqual(len(storage), 0)

    def testDeleteRemovesItemAndIndex(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale = storage.scale(foo=23, bar=42)
        self.assertEqual(len(storage), 1)
        del storage[scale['uid']]
        self.assertEqual(len(storage), 0)

    def testCleanUpOldItemsBBB(self):
        storage = self.storage
        scale_old = storage.scale(factory=self.factory, foo=23, bar=42)
        next_modified = storage.modified() + 1
        storage.modified = lambda: next_modified
        scale_new = storage.scale(factory=self.factory, foo=23, bar=42)
        self.assertEqual(len(storage), 1)
        self.assertEqual(scale_new['uid'] in storage, True)
        self.assertEqual(scale_old['uid'] in storage, False)

        # When modification time is older than a day, too old scales
        # get purged.
        next_modified = storage.modified() + 24 * 60 * 60 * 1000 + 1
        storage.modified = lambda: next_modified
        scale_newer = storage.scale(factory=self.factory, foo=23, bar=42)

        self.assertEqual(scale_newer['uid'] in storage, True)
        self.assertEqual(scale_new['uid'] in storage, False)
        self.assertEqual(scale_old['uid'] in storage, False)
        del storage[scale_newer['uid']]
        self.assertEqual(len(storage), 0)

    def testCleanUpOldItems(self):
        self._provide_dummy_scale_adapter()
        storage = self.storage
        scale_old = storage.scale(foo=23, bar=42)
        next_modified = storage.modified() + 1
        storage.modified = lambda: next_modified
        scale_new = storage.scale(foo=23, bar=42)
        self.assertEqual(len(storage), 1)
        self.assertEqual(scale_new['uid'] in storage, True)
        self.assertEqual(scale_old['uid'] in storage, False)

        # When modification time is older than a day, too old scales
        # get purged.
        next_modified = storage.modified() + 24 * 60 * 60 * 1000 + 1
        storage.modified = lambda: next_modified
        scale_newer = storage.scale(foo=23, bar=42)

        self.assertEqual(scale_newer['uid'] in storage, True)
        self.assertEqual(scale_new['uid'] in storage, False)
        self.assertEqual(scale_old['uid'] in storage, False)
        del storage[scale_newer['uid']]
        self.assertEqual(len(storage), 0)

    def testClearBBB(self):
        storage = self.storage
        storage.scale(factory=self.factory, foo=23, bar=42)
        self.assertEqual(len(storage), 1)
        storage.clear()
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
