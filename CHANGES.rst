Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

3.1.2 (2020-09-07)
------------------

Bug fixes:


- Resolve deprecation warning [gforcada] (#42)


3.1.1 (2020-04-22)
------------------

Bug fixes:


- Minor packaging updates. (#1)


3.1.0 (2020-03-08)
------------------

New features:


- The ``mode`` argument replaces the old, now deprecated, ``direction`` argument.
  The new names are ``contain`` or ``scale-crop-to-fit`` instead of ``down``,
  ``cover`` or ``scale-crop-to-fill`` instead of ``up``
  and ``scale`` instead of ``thumbnail``.
  [fschulze] (#29)
- Added ``calculate_scaled_dimensions`` function to calculate sizes from bare values without actually scaling an image.
  [fschulze]

  Added ``MAX_PIXELS`` constant set to ``8192*8192`` to prevent memory overflow while scaling.
  [fschulze] (#37)


Bug fixes:


- Fix documentation of scaling modes to match it's behavior.
  [thet] (#39)


3.0.3 (2018-11-04)
------------------

Bug fixes:

- reduce warnings in tests [jensens]


3.0.2 (2018-09-28)
------------------

Bug fixes:

- Fix cleanup of image scales in py3
  [pbauer]


3.0.1 (2018-04-03)
------------------

Bug fixes:

- Fix conflict resolution code corner case.
  [gforcada]


3.0 (2017-10-02)
----------------

Breaking changes:

- Restore scale down behaviour from 1.x series without the huge memory usage.
  [fschulze]

New features:

- Handle TIFF images with alpha channels.
  [fschulze]


2.2 (2017-08-27)
----------------

New features:

- Python 3 compatibility.
  [dhavlik]


2.1.2 (2017-05-31)
------------------

Bug fixes:

- Remove unused dependency.
  [gforcada]


2.1.1 (2017-03-29)
------------------

Bug fixes:

- Only convert JPEG to greyscale if they actually are and not when the image
  has less than 256 colors. This bug was introduced in 2.1 with PR #13.
  [fschulze]

- Preserve color profile in scaled images.
  [fschulze]


2.1 (2016-11-01)
----------------

New features:

- Choose an appropriate image mode in order to reduce file size.
  [didrix]

Bug fixes:

- Require the ``six`` package so we can more easily check number types.
  On Python 3 ``long`` has been merged into ``int``.  [maurits]

- When getting an outdated scale, don't throw it away when there is no
  factory.  [maurits]

- Avoid TypeErrors when looking for outdated scales.
  Fixes `issue 12 <https://github.com/plone/plone.scale/issues/12>`_.
  [maurits]

- Catch KeyError when deleting non existing scale.  This can happen in corner cases.
  Fixes `issue 15 <https://github.com/plone/plone.scale/issues/15>`_.
  [maurits]

- Set ``zip_safe=False`` in ``setup.py``.  Otherwise you cannot run
  the tests of the released package because the test runner does not
  find any tests in the egg file.  Note that this is only a problem in
  zc.buildout 1.x: it uses unzip=False by default.  zc.buildout 2.x no
  longer has this option and always unzips eggs.  [maurits]


2.0 (2016-08-12)
----------------

New:

- Assume a width or height of zero is semantically the same as None already was:
  Use the other dimension to scale, calculate the missing one.
  [jensens, thet]

- Scaled GIFs are converted to RGBA PNG images instead of converting them to JPEG.
  [thet, jensens]

Fixes:

- Don't scale images up for direction "down".
  [thet]

- Major housekeeping, code refactored in order to reduce complexicty.
  [jensens]


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
