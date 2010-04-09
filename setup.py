try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages
from os.path import join

version = "1.0a2"
readme = open("README.txt").read().replace(':class:', '').replace(':mod:', '')
changes = open(join("docs", "changes.rst")).read()

setup(name="plone.scale",
      version=version,
      description="Image scaling",
      long_description=readme + "\n" + changes,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords="image scaling",
      author="Wichert Akkerman",
      author_email="wichert@simplon.biz",
      url="",
      license="BSD",
      packages=find_packages(exclude=["ez_setup"]),
      namespace_packages=["plone"],
      include_package_data=True,
      zip_safe=True,
      test_suite="plone.scale",
      install_requires=[
          "PIL",
          "setuptools",
          ],
      extras_require = dict(
          storage = [ "zope.annotation",
                      "zope.component",
                      "zope.interface",
                      "uuid",
                    ],
          ),
      )
