Changelog
=========

1.2 - 2010-07-18
----------------

* Update package metadata.
  [hannosch]

1.1 - 2010-04-20
----------------

* Abort if thumbnail behaviour is requested but either width or height is
  missing. This is nicer than confronting the caller with a PIL exception.
  [wichert]

* Rename the `keep` direction to `thumbnail` to make its behaviour more
  intuitive, but accept `keep` for now.
  [wichert]

1.0 - 2010-04-12
----------------

* Only pull in the uuid distribution in Python versions before 2.5.
  [hannosch]

* Don't declare dependency on PIL.
  [davisagli]

1.0a2 - 2010-04-10
------------------

* Add BSD license text following board decision:
  http://lists.plone.org/pipermail/membership/2009-August/001038.html
  [elro]

* Allow to use PIL's thumbnail algorithm to keep the present aspect ratio.
  [spamsch, witsch]

* Allow to set the quality of the resulting image scales.
  [witsch]

* Refactor storage adapter for image scales to be less dependent on the
  underlying content type.
  [witsch]

1.0a1 - 2009-11-10
------------------

* Initial release
  [wichert]
