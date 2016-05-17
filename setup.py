# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

version = '1.5.0'
readme = open('README.rst').read().replace(':class:', '').replace(':mod:', '')
changes = open('CHANGES.rst').read()

STORAGE_REQUIREMENTS = [
    'zope.annotation',
    'zope.component',
    'zope.interface',
    'Persistence',
]

TESTS_REQUIREMENTS = [
    'Pillow',
    'plone.testing'
]

SPHINX_REQUIREMENTS = [
    'Sphinx',
    'repoze.sphinx.autointerface',
]

setup(
    name='plone.scale',
    version=version,
    description='Image scaling',
    long_description=readme + '\n' + changes,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 5.0',
        'Framework :: Zope2',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='image scaling',
    author='Plone Foundation',
    author_email='plone-developers@lists.sourceforge.net',
    url='https://pypi.python.org/pypi/plone.scale',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=True,
    test_suite='plone.scale',
    install_requires=[
        # We can't actually depend on PIL because not everyone can install it
        # as an egg.
        # 'PIL',
        # 'Pillow'
        'setuptools',
    ],
    extras_require=dict(
        test=TESTS_REQUIREMENTS,
        storage=STORAGE_REQUIREMENTS,
        sphinx=STORAGE_REQUIREMENTS + SPHINX_REQUIREMENTS,
        tests=STORAGE_REQUIREMENTS + TESTS_REQUIREMENTS,
    ),
)
