Introduction
============

This package contains image scaling logic for use in Zope environments. It
supports Zope 2, grok and other systems build on using the Zope ToolKit (ZTK).

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


Usage
=====

The most common way to use *plone.scale* is from a HTML template.
In TAL syntax a typical usage looks like this::

  <img tal:define="scales context/@@image-scaling;
                   thumbnail python:scales.scale('logo', width=64, height=64)"
       tal:attributes="src thumbnail/url;
                       width thumbnail/width;
                       height thumbnail/height" />

This generates a thumbnail of an image field called *logo* with a maximum size
of 64x64 pixels. The dimensions of the resulting image (which might not be
exactly 64x64) are set as attributes on the ``img`` tag to speed up browser
rendering.

If you prefer Genshi syntax and have the ``IImageScaleStorage`` interface
in scope the syntax looks like this::

  <img py:with="thumbnail=IImageScaleStorage(context).scale('logo', width=64, heigh=64)"
       py:attributes="dict(src=thumbnail.url, width=thumbnail.width, height=thumbnail.height" />

