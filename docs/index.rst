.. _index:

***************************************************************
:mod:`plone.scale` -- Image scaling logic
***************************************************************

:Author: Simplon / Wichert Akkerman
:Version: |version|

.. module:: plone.scale
  :synopsis: Plone image scaling framework

:mod:`plone.scale` contains basic image scaling logic for use in Zope
environments. It supports Zope 2, grok and other systems build on using the
Zope ToolKit (ZTK).

Several design goals were used when writing this package: 

- image scaling to any width, height, width&height should be supported
  using both up-scaling and down-scaling. Scaling parameters should never
  be fixed in code. This allows designers to use any image scale they want
  without having to modify python code.

- the result of scaling will be an image along with its new size, not a
  HTML or XHTML tag. We already have excellent tools to generate tags in
  the form of Zope Pagetemplates, Genshi and other template languages that
  are much better suited for this purpose.

In addition several implementation goals were defined:

- image scaling must happen on demand instead of up-front. This reduces
  initial save time and prevents unnecessary scalings from being generated.

- image scaling parameters should not be part of the generated URL. Since
  the number of parameters can change and new parameters may be added in
  the future this would create overly complex URLs and URL parsing.

- no HTML rewriting (such as done by `repoze.bitblt`_) should be required.

- it should be possibly to develop an external storage system which stores
  scaled images externally and returns a URL which bypasses the application
  server. This should be configurable via just a filesystem path & base
  URL.

- minimum number of external dependencies, allowing this package to be
  used in many environments.

- testable without requiring zope.testing. Running `setup.py test` should
  be sufficient.
 
- URLs for scaled images should have an extension which reflects their
  MIME type. This is facilitates cache (and other front-end services)
  configuration.


.. _repoze.bitblt: http://pypi.python.org/pypi/repoze.bitblt
.. todolist::


Contents
==============

.. toctree::
  :maxdepth: 2

  narr/scale
  narr/storage
  changes



Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
