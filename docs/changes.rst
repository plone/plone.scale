Changelog
=========

1.0 - April 12th, 2010
----------------------

* Only pull in the uuid distribution in Python versions before 2.5.
  [hannosch]

* Don't declare dependency on PIL.
  [davisagli]

1.0a2 - April 10th, 2010
------------------------

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

1.0a1 - November 10th, 2009
---------------------------

* Initial release
  [wichert]
