from unittest import TestCase
from operator import itemgetter, setitem, delitem


class AnnotationStorageTests(TestCase):

    @property
    def storage(self):
        from plone.scale.storage import AnnotationStorage
        storage = AnnotationStorage(None)
        storage.modified = lambda: 42
        storage.storage = {}
        return storage

    def factory(self, **kw):
        return 'some data', 'png', (42, 23)

    def testInterface(self):
        from plone.scale.storage import IImageScaleStorage
        storage = self.storage
        self.failUnless(IImageScaleStorage.providedBy(storage))

    def testScaleForNonExistingScaleWithCreation(self):
        storage = self.storage
        scale = storage.scale(factory=self.factory, foo=23, bar=42)
        self.failUnless('uid' in scale)
        self.failUnless('key' in scale)
        self.assertEqual(scale['data'], 'some data')
        self.assertEqual(scale['width'], 42)
        self.assertEqual(scale['height'], 23)
        self.assertEqual(scale['mimetype'], 'image/png')

    def testScaleForNonExistingScaleWithoutCreation(self):
        storage = self.storage
        scale = storage.scale(foo=23, bar=42)
        self.assertEqual(scale, None)

    def testScaleForExistingScale(self):
        storage = self.storage
        scale1 = storage.scale(factory=self.factory, foo=23, bar=42)
        scale2 = storage.scale(factory=self.factory, bar=42, foo=23)
        self.failUnless(scale1 is scale2)
        self.assertEqual(len(storage), 2)

    def testScaleForSimilarScales(self):
        storage = self.storage
        scale1 = storage.scale(factory=self.factory, foo=23, bar=42)
        scale2 = storage.scale(factory=self.factory, bar=42, foo=23, hurz='!')
        self.failIf(scale1 is scale2)
        self.assertEqual(len(storage), 4)

    def testGetItem(self):
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
        self.assertEqual(storage.has_key('one'), False)

    def testPositiveHasKey(self):
        storage = self.storage
        storage.storage.update(one=None)
        self.assertEqual(storage.has_key('one'), True)

    def testDeleteNonExistingItem(self):
        storage = self.storage
        self.assertRaises(KeyError, delitem, storage, 'foo')

    def testDeleteRemovesItemAndIndex(self):
        storage = self.storage
        scale = storage.scale(factory=self.factory, foo=23, bar=42)
        self.assertEqual(len(storage), 2)
        del storage[scale['uid']]
        self.assertEqual(len(storage), 0)


def test_suite():
    from unittest import defaultTestLoader
    return defaultTestLoader.loadTestsFromName(__name__)
