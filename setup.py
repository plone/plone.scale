import sys
from os.path import join
try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages

version = '1.3.3'
readme = open("README.rst").read().replace(':class:', '').replace(':mod:', '')
changes = open(join("docs", "changes.rst")).read()

STORAGE_REQUIREMENTS = [
    "zope.annotation",
    "zope.component",
    "zope.interface",
    "Persistence",
]

SPHINX_REQUIREMENTS = [
    "Sphinx",
    "repoze.sphinx.autointerface",
]

if sys.version_info[:3] < (2, 5, 0):
    # uuid is only required before Python 2.5
    STORAGE_REQUIREMENTS.append("uuid")

setup(name="plone.scale",
      version=version,
      description="Image scaling",
      long_description=readme + "\n" + changes,
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "License :: OSI Approved :: BSD License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
        ],
      keywords="image scaling",
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.scale',
      license="BSD",
      packages=find_packages(exclude=["ez_setup"]),
      namespace_packages=["plone"],
      include_package_data=True,
      zip_safe=True,
      test_suite="plone.scale",
      install_requires=[
          # We can't actually depend on PIL because not everyone can install it
          # as an egg.
          #"PIL",
          "setuptools",
          ],
      extras_require = dict(
          storage = STORAGE_REQUIREMENTS,
          sphinx = STORAGE_REQUIREMENTS + SPHINX_REQUIREMENTS,
          ),
      )
