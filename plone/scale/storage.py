# -*- coding: utf-8 -*-
from persistent.dict import PersistentDict
from plone.scale.interfaces import IImageScaleFactory
from UserDict import DictMixin
from uuid import uuid4
from ZODB.POSException import ConflictError
from zope.annotation import IAnnotations
from zope.interface import implementer
from zope.interface import Interface

import logging
import pprint
import warnings


logger = logging.getLogger('plone.scale')
# Keep old scales around for this amount of milliseconds.
# This is one day:
KEEP_SCALE_MILLIS = 24 * 60 * 60 * 1000


class IImageScaleStorage(Interface):
    """ This is an adapter for image content which can store, retrieve and
        generate image scale data. It provides a dictionary interface to
        existing image scales using the scale id as key. To find or create a
        scale based on its scaling parameters use the :meth:`scale` method. """

    def __init__(context, modified=None):
        """ Adapt the given context item and optionally provide a callable
            to return a representation of the last modification date, which
            can be used to invalidate stored scale data on update. """

    def scale(factory=None, **parameters):
        """ Find image scale data for the given parameters or create it if
            a factory was provided.  The parameters will be passed back to
            the factory method, which is expected to return a tuple
            containing a representation of the actual image scale data (i.e.
            a string or file-like object) as well as the image's format and
            dimensions.  For convenience, this happens to match the return
            value of `scaleImage`, but makes it possible to use different
            storages, i.e. ZODB blobs """

    def __getitem__(uid):
        """ Find image scale data based on its uid. """


class ScalesDict(PersistentDict):

    def raise_conflict(self, saved, new):
        logger.info('Conflict')
        logger.debug('saved\n' + pprint.pformat(saved))
        logger.debug('new\n' + pprint.pformat(new))
        raise ConflictError

    def _p_resolveConflict(self, oldState, savedState, newState):
        logger.debug('Resolve conflict')
        old = oldState['data']
        saved = savedState['data']
        new = newState['data']
        added = []
        modified = []
        deleted = []
        for key, value in new.items():
            if key not in old:
                added.append(key)
            elif value['modified'] != old[key]['modified']:
                modified.append(key)
            # else:
                # unchanged
        for key in old:
            if key not in new:
                deleted.append(key)
        for key in deleted:
            if ((key in saved) and
                    (old[key]['modified'] == saved[key]['modified'])):
                # unchanged by saved, deleted by new
                logger.debug('deleted %s' % repr(key))
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
                logger.debug('added %s' % repr(key))
                saved[key] = new[key]
        for key in modified:
            if key not in saved:
                # deleted by saved, modified by new
                self.raise_conflict(saved[key], new[key])
            elif saved[key]['modified'] != old[key]['modified']:
                # modified by saved, modified by new
                self.raise_conflict(saved[key], new[key])
            else:
                # unchanged in saved, modified by new
                logger.debug('modified %s' % repr(key))
                saved[key] = new[key]
        return dict(data=saved)


@implementer(IImageScaleStorage)
class AnnotationStorage(DictMixin):
    """ An abstract storage for image scale data using annotations and
        implementing :class:`IImageScaleStorage`. Image data is stored as an
        annotation on the object container, i.e. the image. This is needed
        since not all images are themselves annotatable. """

    def __init__(self, context, modified=None):
        self.context = context
        self.modified = modified

    def _modified_since(self, since):
        if since is None:
            return False
        elif self.modified_time is None:
            return False
        else:
            return self.modified_time > since

    @property
    def modified_time(self):
        if self.modified is not None:
            return self.modified()
        else:
            return None

    def __repr__(self):
        name = self.__class__.__name__
        return '<%s context=%r>' % (name, self.context)

    __str__ = __repr__

    @property
    def storage(self):
        annotations = IAnnotations(self.context)
        scales = annotations.setdefault(
            'plone.scale',
            ScalesDict()
        )
        if not isinstance(scales, ScalesDict):
            # migrate from PersistentDict to ScalesDict
            new_scales = ScalesDict(scales)
            annotations['plone.scale'] = new_scales
            return new_scales
        return scales

    def hash(self, **parameters):
        return tuple(sorted(parameters.items()))

    def get_info_by_hash(self, hash):
        for value in self.storage.values():
            if value['key'] == hash:
                return value

    def scale(self, factory=None, **parameters):
        key = self.hash(**parameters)
        storage = self.storage
        info = self.get_info_by_hash(key)
        if info is not None and self._modified_since(info['modified']):
            del storage[info['uid']]
            # invalidate when the image was updated
            info = None
        elif info is not None:
            return info

        scaling_factory = IImageScaleFactory(self.context, None)

        # BBB/Deprecation handling
        if factory is not None:
            if scaling_factory is not None:
                warnings.warn(
                    'Deprecated usage of factory in plone.scale. '
                    'Factory is passed to plone.scale but also an adapter '
                    'was found. No way to really decide which one to execute.'
                    'To be nice and with a look at backward compatibility the '
                    'passed one is used.',
                    DeprecationWarning
                )
            else:
                warnings.warn(
                    'Deprecated usage of factory in plone.scale. Provide an '
                    'adapter for the factory instead. The kwarg will be '
                    'dropped with plone.scale 3.0',
                    DeprecationWarning
                )
            result = factory(**parameters)
        elif scaling_factory is not None:
            # this is what we want, keep this after deprecaton phase
            result = scaling_factory(**parameters)
        else:
            # adaption error, nor a factory was passed.
            # BBB behavior here is to return None
            # nevertheless we warn!
            warnings.warn(
                'Could not adapt context to IImageScaleFactory nor a '
                'deprecated BBB factory callable was provided.'
                'Assume None return value as it was before.'
            )
            return None

        if result is not None:
            # storage will be modified:
            # good time to also cleanup
            self._cleanup()
            data, format_, dimensions = result
            width, height = dimensions
            uid = str(uuid4())
            info = dict(
                uid=uid,
                data=data,
                width=width,
                height=height,
                mimetype='image/{0}'.format(format_.lower()),
                key=key,
                modified=self.modified_time,
            )
            storage[uid] = info
        return info

    def _cleanup(self):
        storage = self.storage
        modified_time = self.modified_time
        for key, value in storage.items():
            # remove info stored by tuple keys
            # before refactoring
            if isinstance(key, tuple):
                del storage[key]
            # clear cache from scales older than one day
            elif (modified_time and
                    value['modified'] < modified_time - KEEP_SCALE_MILLIS):
                del storage[key]

    def __getitem__(self, uid):
        return self.storage[uid]

    def __setitem__(self, id, scale):
        raise RuntimeError('New scales have to be created via scale()')

    def __delitem__(self, uid):
        del self.storage[uid]

    def __iter__(self):
        return iter(self.storage)

    def keys(self):
        return self.storage.keys()

    def has_key(self, uid):
        return uid in self.storage

    __contains__ = has_key

    def clear(self):
        self.storage.clear()
