from pathlib import Path
from setuptools import setup


version = "5.0.0a2"

long_description = (
    f"{Path('README.rst').read_text()}\n{Path('CHANGES.rst').read_text()}"
)

STORAGE_REQUIREMENTS = [
    "ZODB",
    "persistent",
]

TEST_REQUIREMENTS = [
    "zope.component",
    "plone.testing[test]",
]

setup(
    name="plone.scale",
    version=version,
    description="Image scaling",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="image scaling",
    author="Plone Foundation",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/plone.scale",
    license="BSD",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "Pillow",
        "lxml",
        "zope.annotation",
        "zope.interface",
    ],
    extras_require=dict(
        storage=STORAGE_REQUIREMENTS,
        test=STORAGE_REQUIREMENTS + TEST_REQUIREMENTS,
    ),
)
