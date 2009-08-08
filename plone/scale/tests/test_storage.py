import operator
import unittest


class BaseAnnotationStorageTests(unittest.TestCase):
    def createStorage(self):
        from plone.scale.storage import BaseAnnotationStorage
        storage=BaseAnnotationStorage()
        storage.fieldname="fieldname"
        storage.annotations={}
        return storage

    def testInterface(self):
        from zope.interface.verify import verifyObject
        from plone.scale.storage import IImageScaleStorage
        storage=self.createStorage()
        self.failUnless(verifyObject(IImageScaleStorage, storage))

    def testGetItemWithoutAnnotations(self):
        storage=self.createStorage()
        self.assertRaises(KeyError, operator.itemgetter("key"), storage)

    def testGetItem(self):
        from plone.scale.storage import IImageScale
        from zope.interface.verify import verifyObject
        storage=self.createStorage()
        marker=[]
        storage.annotations["plone.scale.fieldname.one"]=dict(
                dimensions=(100,200), mimetype="image/png",
                size=76543, data=marker)
        scale=storage["one"]
        self.failUnless(verifyObject(IImageScale, scale))
        self.assertEqual(scale.id, "one")
        self.assertEqual(scale.dimensions, (100,200))
        self.assertEqual(scale.mimetype, "image/png")
        self.assertEqual(scale.size, 76543)
        self.failUnless(hasattr(scale, "url"), True)
        self.failUnless(isinstance(scale.url), str)

    def testSetItemNotAllowed(self):
        storage=self.createStorage()
        self.assertRaises(RuntimeError, operator.setitem, storage, "key", None)

    def testIterateWithoutAnnotations(self):
        storage=self.createStorage()
        self.assertEqual(list(storage), [])

    def testIterate(self):
        import types
        storage=self.createStorage()
        storage.annotations["plone.scale.fieldname"]=[("one", None), ("two", None)]
        generator=iter(storage)
        self.failUnless(isinstance(generator, types.GeneratorType))
        self.assertEqual(list(generator), ["one", "two"])

    def testKeys(self):
        storage=self.createStorage()
        storage.annotations["plone.scale.fieldname"]=[("one", None), ("two", None)]
        self.failUnless(isinstance(storage.keys(), list))
        self.assertEqual(storage.keys(), ["one", "two"])

    def testNegativeHasKey(self):
        storage=self.createStorage()
        self.assertEqual(storage.has_key("one"), False)

    def testPositiveHasKey(self):
        storage=self.createStorage()
        storage.annotations["plone.scale.fieldname.one"]=None
        self.assertEqual(storage.has_key("one"), True)

    def testDeleteNonExistingItem(self):
        storage=self.createStorage()
        self.assertRaises(KeyError, operator.delitem, storage, "key")

    def testDeleteRemovesItemAndIndex(self):
        storage=self.createStorage()
        storage.annotations["plone.scale.fieldname"]=[("key", None), ("other", None)]
        storage.annotations["plone.scale.fieldname.key"]=None
        storage.annotations["plone.scale.fieldname.other"]=None
        del storage["key"]
        self.assertEqual(storage.annotations["plone.scale.fieldname"], [("other", None)])
        self.failUnless("plone.scale.fieldname.key" not in storage.annotations)


