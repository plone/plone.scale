from .scale import calculate_scaled_dimensions
from .scale import get_scale_mode
from collections.abc import MutableMapping
from persistent.dict import PersistentDict
from plone.scale.interfaces import IImageScaleFactory
from time import time
from ZODB.POSException import ConflictError
from zope.annotation import IAnnotations
from zope.interface import implementer
from zope.interface import Interface

import hashlib
import logging
import pprint


try:
    from plone.protect.utils import safeWrite
except ImportError:
    safeWrite = None

logger = logging.getLogger("plone.scale")
# Keep old scales around for this amount of milliseconds.
# This is one day:
KEEP_SCALE_MILLIS = 24 * 60 * 60 * 1000

# Number types are float and int, and on Python 2 also long.
number_types = [float]
number_types.extend((int,))
number_types = tuple(number_types)


class IImageScaleStorage(Interface):
    """This is an adapter for image content which can store, retrieve and
    generate image scale data. It provides a dictionary interface to
    existing image scales using the scale id as key. To find or create a
    scale based on its scaling parameters use the :meth:`scale` method."""

    def __init__(context, modified=None):
        """Adapt the given context item and optionally provide a callable
        to return a representation of the last modification date, which
        can be used to invalidate stored scale data on update."""

    def pre_scale(**parameters):
        """Pre-register a unique id for a scale, without actually scaling.

        In other words: no use of Pillow allowed.
        """

    def scale(**parameters):
        """Find image scale data for the given parameters or create it.

        We will look for an IImageScaleFactory for the context, and pass
        the parameters.  This factory is expected to return a tuple
        containing a representation of the actual image scale data (i.e.
        a string or file-like object) as well as the image's format and
        dimensions.  For convenience, this happens to match the return
        value of `scaleImage`, but makes it possible to use different
        storages, i.e. ZODB blobs"""

    def __getitem__(uid):
        """Find image scale data based on its uid."""

    def get_or_generate(uid):
        """Find image scale data based on its uid, or generate it.

        Only uids pre-generated by the pre_scale method should be accepted.

        Outdated scales may be returned: this method is called when requesting a scale
        on a cached, unique url.  An old cached page may still point to this.
        """


class ScalesDict(PersistentDict):
    def raise_conflict(self, saved, new):
        logger.info("Conflict")
        logger.debug("saved\n" + pprint.pformat(saved))
        logger.debug("new\n" + pprint.pformat(new))
        raise ConflictError

    def _p_resolveConflict(self, oldState, savedState, newState):
        logger.debug("Resolve conflict")
        old = oldState["data"]
        saved = savedState["data"]
        new = newState["data"]
        added = []
        modified = []
        deleted = []
        for key, value in new.items():
            if key not in old:
                added.append(key)
            elif value["modified"] != old[key]["modified"]:
                modified.append(key)
            # else:
            # unchanged
        for key in old:
            if key not in new:
                deleted.append(key)
        for key in deleted:
            if key in saved:
                if old[key]["modified"] == saved[key]["modified"]:
                    # unchanged by saved, deleted by new
                    logger.debug("deleted %s" % repr(key))
                    del saved[key]
                else:
                    # modified by saved, deleted by new
                    self.raise_conflict(saved[key], new[key])
        for key in added:
            if key in saved:
                # added by saved, added by new
                self.raise_conflict(saved[key], new[key])
            else:
                # not in saved, added by new
                logger.debug("added %s" % repr(key))
                saved[key] = new[key]
        for key in modified:
            if key not in saved:
                # deleted by saved, modified by new
                self.raise_conflict(saved[key], new[key])
            elif saved[key]["modified"] != old[key]["modified"]:
                # modified by saved, modified by new
                self.raise_conflict(saved[key], new[key])
            else:
                # unchanged in saved, modified by new
                logger.debug("modified %s" % repr(key))
                saved[key] = new[key]
        return dict(data=saved)


@implementer(IImageScaleStorage)
class AnnotationStorage(MutableMapping):
    """An abstract storage for image scale data using annotations and
    implementing :class:`IImageScaleStorage`. Image data is stored as an
    annotation on the object container, i.e. the image. This is needed
    since not all images are themselves annotatable."""

    def __init__(self, context, modified=None):
        self.context = context
        self.modified = modified

    def _modified_since(self, since, offset=0):
        # offset gets subtracted from the main modified time: this allows to
        # keep scales for a bit longer if needed, even when the main image has
        # changed.
        if since is None:
            return False
        modified_time = self.modified_time
        if modified_time is None:
            return False
        # We expect a number, but in corner cases it can be
        # something else entirely.
        # https://github.com/plone/plone.scale/issues/12
        if not isinstance(modified_time, number_types):
            return False
        if not isinstance(since, number_types):
            return False
        modified_time = modified_time - offset
        return modified_time > since

    @property
    def modified_time(self):
        if self.modified is not None:
            return self.modified()
        else:
            return None

    def __repr__(self):
        name = self.__class__.__name__
        return f"<{name} context={self.context!r}>"

    __str__ = __repr__

    @property
    def storage(self):
        annotations = IAnnotations(self.context)
        if "plone.scale" not in annotations:
            annotations["plone.scale"] = ScalesDict()
            if safeWrite is not None:
                safeWrite(self.context)
        scales = annotations["plone.scale"]
        if not isinstance(scales, ScalesDict):
            # migrate from PersistentDict to ScalesDict
            new_scales = ScalesDict(scales)
            annotations["plone.scale"] = new_scales
            if safeWrite is not None:
                safeWrite(self.context)
            return new_scales
        return scales

    def hash(self, **parameters):
        return tuple(sorted(parameters.items()))

    def unhash(self, hash_key):
        return dict(hash_key)

    def get_info_by_hash(self, hash):
        for value in self.storage.values():
            if value["key"] == hash:
                return value

    def hash_key(self, **parameters):
        if "modified" in parameters:
            del parameters["modified"]
        key = self.hash(modified=self.modified_time, **parameters)
        fieldname = parameters.get("fieldname", "image")
        dimension = parameters.get("width", parameters.get("scale"))
        if dimension is None:
            dimension = 0
        hash_key = hashlib.md5(str(key).encode("utf-8")).hexdigest()
        # We return a uid that is recognizable when you inspect a url in html or
        # on the network tab: you immediately see for which field this is and what
        # the width is.  This helps during debugging/testing.
        return f"{fieldname}-{dimension}-{hash_key}"

    def pre_scale(self, **parameters):
        # This does *not* create a scale.
        # It only prepares info.
        logger.debug(f"Pre scale {parameters}")
        uid = self.hash_key(**parameters)
        # self.clear()
        # logger.debug(list(self.storage.keys()))
        info = self.get(uid)
        if info is not None and not self._modified_since(info["modified"]):
            logger.debug(f"Pre scale returns old {info}")
            return info

        scaling_factory = IImageScaleFactory(self.context, None)
        if scaling_factory is None:
            # There is nothing we can do.
            return
        fieldname = parameters.get("fieldname", None)
        value = scaling_factory.get_original_value(fieldname=fieldname)
        if value is None:
            # Either an empty value, or the field does not exist.
            return

        # There is no info, or it is outdated.  Recreate the scale info.
        # We need width and height for various reasons.
        # Start with a basis.
        width = parameters.get("width")
        height = parameters.get("height")
        orig_width, orig_height = value.getImageSize()
        mode = get_scale_mode(
            parameters.get("direction") or parameters.get("mode") or "contain"
        )
        width, height = calculate_scaled_dimensions(
            orig_width, orig_height, width, height, mode
        )
        mimetype = value.contentType
        key = self.hash(**parameters)
        info = dict(
            uid=uid,
            key=key,
            modified=int(time() * 1000),
            mimetype=mimetype,
            data=None,
            width=width,
            height=height,
        )
        self.storage[uid] = info
        logger.debug(f"Pre scale returns new {info}")
        return info

    def generate_scale(self, uid=None, **parameters):
        logger.debug("Generating scale...")
        scaling_factory = IImageScaleFactory(self.context, None)
        if scaling_factory is None:
            # There is nothing we can do.
            return
        result = scaling_factory(**parameters)
        if result is None:
            return
        # storage will be modified:
        # good time to also cleanup
        fieldname = parameters.get("fieldname")
        self._cleanup(fieldname=fieldname)
        data, format_, dimensions = result
        width, height = dimensions
        if uid is None:
            uid = self.hash_key(**parameters)
        key = self.hash(**parameters)
        info = dict(
            uid=uid,
            data=data,
            width=width,
            height=height,
            mimetype=f"image/{format_.lower()}",
            key=key,
            modified=self.modified_time or int(time() * 1000),
        )
        if fieldname:
            info["fieldname"] = fieldname
        self.storage[uid] = info
        logger.debug(f"Generated scale: {info}")
        return info

    def scale(self, **parameters):
        logger.debug(f"scale called with {parameters}")
        uid = self.hash_key(**parameters)
        info = self.get(uid)
        if info is None:
            # Might be on old-style uuid4 scale
            key = self.hash(**parameters)
            info = self.get_info_by_hash(key)
        if (
            info is not None
            and info.get("data") is not None
            and not self._modified_since(info["modified"])
        ):
            logger.debug(f"scale found existing info {info}")
            return info
        return self.generate_scale(**parameters)

    def get_or_generate(self, name):
        logger.debug(f"get or generate {name}")
        info = self.get(name)
        if info is None:
            logger.debug(f"get or generate {name} not found")
            return
        if info is not None and info.get("data") is not None:
            # We could check 'self._modified_since(info["modified"])'.
            # But in fact we do not care if this scale is outdated.
            # A cached page may point to this, and the browser requests it now.
            logger.debug(f"get or generate {name} found {info}")
            return info
        # This scale has not been generated yet.
        # Get the parameters used when pre-registering this scale.
        parameters = self.unhash(info["key"])
        return self.generate_scale(uid=name, **parameters)

    def _cleanup(self, fieldname=None):
        storage = self.storage
        modified_time = self.modified_time
        if modified_time is None:
            return
        if not isinstance(modified_time, number_types):
            # https://github.com/plone/plone.scale/issues/12
            return
        for key, value in list(storage.items()):
            # remove info stored by tuple keys
            # before refactoring
            if isinstance(key, tuple):
                del self[key]
            if fieldname and "fieldname" in value and value["fieldname"] != fieldname:
                # Leave scales for other fieldnames alone.
                # self.modified may have nothing to do with that field.
                continue
            # clear cache from scales older than one day
            elif self._modified_since(value["modified"], offset=KEEP_SCALE_MILLIS):
                del self[key]

    def __getitem__(self, uid):
        return self.storage[uid]

    def __setitem__(self, id, scale):
        raise RuntimeError("New scales have to be created via scale()")

    def __delitem__(self, uid):
        try:
            del self.storage[uid]
        except KeyError:
            # This should not happen, but it apparently can happen in corner
            # cases.  See https://github.com/plone/plone.scale/issues/15
            logger.warning("Could not delete key %s from storage.", uid)

    def __iter__(self):
        return iter(self.storage)

    def __len__(self):
        return len(self.keys())

    def keys(self):
        return self.storage.keys()

    def has_key(self, uid):
        return uid in self.storage

    __contains__ = has_key

    def clear(self):
        self.storage.clear()
