import operator
import unittest


class AnnotationStorageTests(unittest.TestCase):
    def createStorage(self):
        from plone.scale.storage import AnnotationStorage
        storage=AnnotationStorage()
        storage.fieldname="fieldname"
        storage.annotations={}
        return storage

    def testInterface(self):
        from zope.interface.verify import verifyObject
        from plone.scale.storage import IImageScaleStorage
        from plone.scale.storage import AnnotationStorage
        storage=self.createStorage()
        self.failUnless(verifyObject(IImageScaleStorage, storage))

    def testGetItemWithoutAnnotations(self):
        storage=self.createStorage()
        self.assertRaises(KeyError, operator.itemgetter("key"), storage)

    def testGetItem(self):
        from plone.scale.storage import IImageScale
        from zope.interface.verify import verifyObject
        storage=self.createStorage()
        storage.annotations["plone.scale.fieldname"]=[
                ("one",
                 dict(width=100, height=200, direction="up"),
                 dict(dimensions=(100,200), mimetype="image/png", size=76543))]
        scale=storage["one"]
        self.failUnless(verifyObject(IImageScale, scale))
        self.assertEqual(scale.id, "one")
        self.assertEqual(scale.width, 100)
        self.assertEqual(scale.height, 200)
        self.assertEqual(scale.mimetype, "image/png")
        self.assertEqual(scale.size, 76543)
        self.failUnless(hasattr(scale, "url"), True)
        self.failUnless(isinstance(scale.url, str))

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
        storage.annotations["plone.scale.one"]=None
        self.assertEqual(storage.has_key("one"), True)

    def testDeleteNonExistingItem(self):
        storage=self.createStorage()
        self.assertRaises(KeyError, operator.delitem, storage, "key")

    def testDeleteRemovesItemAndIndex(self):
        storage=self.createStorage()
        storage.annotations["plone.scale.fieldname"]=[("key1", None), ("key2", None)]
        storage.annotations["plone.scale.key1"]=("fieldname", None)
        storage.annotations["plone.scale.key2"]=("fieldname", None)
        del storage["key1"]
        self.assertEqual(storage.annotations["plone.scale.fieldname"], [("key2", None)])
        self.failUnless("plone.scale.key1" not in storage.annotations)

    def testGetScaleForExistingScale(self):
        from plone.scale.storage import IImageScale
        storage=self.createStorage()
        storage.annotations["plone.scale.fieldname"]=[
                ("one",
                 dict(width=100, height=200, direction="up"),
                 dict(dimensions=(100,200), mimetype="image/png", size=76543))]
        scale=storage.scale("fieldname", width=100, height=200, direction="up")
        self.failUnless(IImageScale.providedBy(scale))
        self.assertEqual(scale.width, 100)
        self.assertEqual(scale.height, 200)
        self.assertEqual(scale.id, "one")

    def testGetScaleForNonExistingScaleWithoutCreation(self):
        storage=self.createStorage()
        scale=storage.scale("fieldname", width=100, height=200, direction="up", create=False)
        self.failUnless(scale is None)

    def testGetScaleForNonExistingScaleWithCreation(self):
        from plone.scale.tests.test_scale import PNG
        from plone.scale.storage import IImageData
        from zope.component import getGlobalSiteManager
        from zope.component import adapts
        from zope.interface import implements

        storage=self.createStorage()
        class Context:
            logo = PNG
        storage.context=Context()

        class NullAdapter:
            implements(IImageData)
            adapts(str)
            def __init__(self, data):
                self.data=data

        gsm=getGlobalSiteManager()
        gsm.registerAdapter(NullAdapter)
        try:
            scale=storage.scale("logo", width=100, height=200, direction="up", create=True)
            self.failUnless(scale is not None)
        finally:
            gsm.unregisterAdapter(NullAdapter)


