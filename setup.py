from setuptools import setup, find_packages

version = '1.4.2'
readme = open("README.rst").read().replace(':class:', '').replace(':mod:', '')
changes = open("CHANGES.rst").read()

STORAGE_REQUIREMENTS = [
    "zope.annotation",
    "zope.component",
    "zope.interface",
    "Persistence",
]

TESTS_REQUIREMENTS = [
    "Pillow",
]

SPHINX_REQUIREMENTS = [
    "Sphinx",
    "repoze.sphinx.autointerface",
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
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Zope2",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    keywords="image scaling",
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.python.org/pypi/plone.scale',
    license="BSD",
    packages=find_packages(exclude=["ez_setup"]),
    namespace_packages=["plone"],
    include_package_data=True,
    zip_safe=False,
    test_suite="plone.scale",
    install_requires=[
        # We can't actually depend on PIL because not everyone can install it
        # as an egg.
        # "PIL",
        "setuptools",
    ],
    extras_require=dict(
        storage=STORAGE_REQUIREMENTS,
        sphinx=STORAGE_REQUIREMENTS + SPHINX_REQUIREMENTS,
        tests=STORAGE_REQUIREMENTS + TESTS_REQUIREMENTS,
    ),
)
