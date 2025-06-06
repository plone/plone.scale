Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

4.2.0 (2025-04-04)
------------------

New features:


- Add method to 'scale' SVGs by modifying display size and viewbox. [jensens[ (#68)


4.1.4 (2025-03-07)
------------------

Bug fixes:


- Fixed scaling of PNG images with grayscale palettes, causing loss of transparency and resulting in black scaled images [rohnsha0] (#43)
- Make sure smallest dimension is at least 1px. @MrTango, @rohnsha0 (#112)


Internal:


- Remove old way to run tests with setuptools [gforcada]
- Update configuration files.
  [plone devs]


4.1.3 (2024-06-13)
------------------

Bug fixes:


- Set PIL.ImageFile.LOAD_TRUNCATED_IMAGES = True to try to load damaged images. @davisagli (#14)


4.1.2 (2024-03-22)
------------------

Bug fixes:


- If width and height are given, ignore the scale parameter when determining the unique id of a scale. @wesleybl (#92)


4.1.1 (2024-01-31)
------------------

Bug fixes:


- Fix incompatibility with Pillow 10.1+.
  Instead of setting ``image.mode``, we call ``image.convert``.
  This works in Pillow 9 and 10.
  [maurits] (#89)


4.1.0 (2023-10-25)
------------------

New features:


- Keep scaled WEBP images in WEBP format instead of converting to JPEG. @mamico (#85)


4.0.2 (2023-10-07)
------------------

Bug fixes:


- Fix KeyError in ScalesDict conflict resolution. @davisagli (#84)


Internal:


- Update configuration files.
  [plone devs] (cfffba8c)


4.0.1 (2023-03-14)
------------------

Internal:


- Update configuration files.
  [plone devs] (a533099d)


Tests


- Tox: explicitly test only the ``plone.scale`` package.  [maurits] (#50)


4.0.0 (2022-11-26)
------------------

Bug fixes:


- Test with Python 3.11.  [maurits] (#311)
- Require Python 3.7 or higher.  [maurits] (#600)


4.0.0b5 (2022-10-20)
--------------------

New features:


- Add support for animated GIFs @reebalazs (#69)


4.0.0b4 (2022-10-03)
--------------------

Breaking changes:


- No longer test Plone 5.2 on 3.6 and Plone 6.0 on 3.7.
  [maurits] (#3637)


Bug fixes:


- Use "scale" mode as default.
  This cleans up more confusion between mode and direction.
  See also `plone.namedfile issue 102 <https://github.com/plone/plone.namedfile/issues/102>`_.
  Previously our definition of the ``IImageScaleFactory`` interface had the deprecated ``direction="thumbnail"``.
  Other parts used ``mode="contain"`` by default, which does cropping, where in Plone we are used to simple scaling almost everywhere.
  [maurits] (#102)


4.0.0b3 (2022-07-19)
--------------------

Bug fixes:


- Fixed getting original data for a tile.
  [maurits] (#64)


4.0.0b2 (2022-07-14)
--------------------

Bug fixes:


- Fix to ensure that when a scale that was registered using `pre_scale` is
  later actually generated by `get_or_generate`, it is stored with the same
  uid as the placeholder info that was stored by `pre_scale`. This avoids
  an issue where the same scale was generated repeatedly.
  [davisagli] (#60)


4.0.0b1 (2022-06-23)
--------------------

New features:


- Pre scale: store non-random uid to prepare space for a scale.
  You call ``pre_scale`` to pre-register the scale with a unique id
  without actually doing any scaling with Pillow.
  When you later call the ``scale`` method, the scale is generated.
  You can still call ``scale`` directly without first calling ``pre_scale``.
  [maurits] (#57)
- Mark as plone.protect's safeWrite AnnotationStorage.
  Precondition for https://github.com/plone/plone.namedfile/pull/117.
  [mamico] (#58)


Bug fixes:


- Minor cleanup: isort, black.  [maurits] (#59)


4.0.0a4 (2022-05-26)
--------------------

Bug fixes:


- Fix cropping when the height is not limited.
  Create a square then.
  Not limited means: 65000 or larger, or zero or lower.
  [maurits] (#53)
- Fix cleanup of scales: only throw away outdated scales of the same field.
  [maurits] (#55)


4.0.0a3 (2022-05-09)
--------------------

Bug fixes:


- Fixed ``DeprecationWarning`` with Pillow 9.1.0 for ``ANTIALIAS``.
  Use ``Resampling.LANCZOS``, falling back to ``ANTIALIAS`` on older Pillows.
  [maurits] (#49)


4.0.0a2 (2022-03-09)
--------------------

Breaking changes:


- Removed deprecated ``factory`` argument from ``scale`` method.
  This is in the ``AnnotationStorage`` class and the ``IImageScaleStorage`` interface.
  This was already scheduled for removal in ``plone.scale`` 3.0, but was kept longer.
  Fixes `issue 47 <https://github.com/plone/plone.scale/issues/47>`_.
  [maurits] (#47)


4.0.0a1 (2022-02-23)
--------------------

Breaking changes:


- Removed docs directory and sphinx extra.
  The docs were last updated in 2010, and the maybe still relevant parts already copied to the readme.
  [maurits] (#44)
- Removed ``tests`` extra, kept only ``test`` extra and ``storage``.
  Swapped packages slightly between those two extras.
  For ``storage`` we depend on ``persistent`` and ``ZODB``.
  [maurits] (#44)
- Depend on Pillow.
  Originally we did not officially depend on it (or PIL) "because not everyone can install it as an egg".
  It seems time to grow up here.
  [maurits] (#44)
- Removed Python 2 support.  Only Python 3.6+ supported now.
  Still works on Plone 5.2.
  [maurits] (#44)


New features:


- Add tox.ini with mxdev.
  Test with GitHub Actions on Plone 5.2 Py + 3.6-3.8 and Plone 6.0 + Py 3.7-3.10.
  [maurits] (#44)


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
  If addons want to provide alternative methods to scale (i.e. cropping),
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
