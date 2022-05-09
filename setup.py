from setuptools import find_packages
from setuptools import setup


version = "4.0.0a3"
with open("README.rst") as myfile:
    readme = myfile.read()
with open("CHANGES.rst") as myfile:
    changes = myfile.read()

STORAGE_REQUIREMENTS = [
    "ZODB",
    "zope.annotation",
    "zope.interface",
    "persistent",
]

# "zope.configuration",
TEST_REQUIREMENTS = [
    "zope.component",
    "zope.configuration",
    "plone.testing",
]

setup(
    name="plone.scale",
    version=version,
    description="Image scaling",
    long_description=readme + "\n" + changes,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 4",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    keywords="image scaling",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.scale",
    license="BSD",
    packages=find_packages(),
    namespace_packages=["plone"],
    include_package_data=True,
    zip_safe=False,
    test_suite="plone.scale",
    install_requires=[
        "Pillow",
        "setuptools",
    ],
    extras_require=dict(
        storage=STORAGE_REQUIREMENTS,
        test=STORAGE_REQUIREMENTS + TEST_REQUIREMENTS,
    ),
)
