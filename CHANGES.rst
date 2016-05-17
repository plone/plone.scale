Changelog
=========


1.5.0 (2016-05-18)
------------------

New:

- Use an adapter to lookup the actual factory for scaling.
  Deprecated passing the factory as named parameter along,
  because this had not enough flexibility:
  If addons want to provide alterative methods to scale (i.e. cropping),
  now a specific adapter can perform the work.
  [jensens]

Fixes:

- Minor housekeeping.
  [jensens]


1.4.1 (2016-02-12)
------------------

Fixes:

- Fix KeyError in storage.AnnotationStorage._cleanup when attempting
  to delete the storage for the same key twice.
  [fulv]


1.4 (2015-12-07)
----------------

New:

- Resolve conflicts raised when accessing multiple scales concurrently.
  [gotcha]

- Refactored scale storage.
  [gotcha]


1.3.5 (2015-03-10)
------------------

- PIL thumbnail does not work for magnifying images (when scaling up).
  Use resize instead. [sureshvv]


1.3.4 (2014-09-07)
------------------

- When a scale is outdated, discard all image scales that are more
  than a day older than the context.
  Refs https://dev.plone.org/ticket/13791
  [maurits]

- Make sure deleting items or clearing a complete storage works.
  Deleting one item would often delete a linked second item, which
  made it hard to remove several items at once.
  [maurits]


1.3.3 (2014-01-27)
------------------

- Discard old image scales if item was modified.
  Refs https://dev.plone.org/ticket/13791
  [gforcada]

- Generate Progressive JPEG.
  [kroman0]


1.3.2 (2013-05-23)
------------------

- Added a marker interface for scaled image quality.
  Refs http://dev.plone.org/plone/ticket/13337
  [khink]


1.3.1 (2013-04-06)
------------------

- Cropped images are now centralised vertically as well as horizontally [mattss]


1.3 (2013-01-17)
----------------

- Add MANIFEST.in.
  [WouterVH]

- Break up `scaleImage`, so that its scaling-related parts can be applied
  to instances of `PIL.Image` for further processing.
  [witsch]


1.2.2 - 2010-09-28
------------------

- Re-release to fix bad egg created for 1.2.1.
  Refs http://dev.plone.org/plone/ticket/11154
  [witsch]


1.2.1 - 2010-08-18
------------------

- Convert CMYK to RGB, allowing for web previews of print images.
  [tomster]


1.2 - 2010-07-18
----------------

- Update package metadata.
  [hannosch]


1.1 - 2010-04-20
----------------

- Abort if thumbnail behaviour is requested but either width or height is
  missing. This is nicer than confronting the caller with a PIL exception.
  [wichert]

- Rename the `keep` direction to `thumbnail` to make its behaviour more
  intuitive, but accept `keep` for now.
  [wichert]


1.0 - 2010-04-12
----------------

- Only pull in the uuid distribution in Python versions before 2.5.
  [hannosch]

- Don't declare dependency on PIL.
  [davisagli]


1.0a2 - 2010-04-10
------------------

- Add BSD license text following board decision:
  http://lists.plone.org/pipermail/membership/2009-August/001038.html
  [elro]

- Allow to use PIL's thumbnail algorithm to keep the present aspect ratio.
  [spamsch, witsch]

- Allow to set the quality of the resulting image scales.
  [witsch]

- Refactor storage adapter for image scales to be less dependent on the
  underlying content type.
  [witsch]


1.0a1 - 2009-11-10
------------------

- Initial release
  [wichert]
