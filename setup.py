from setuptools import setup, find_packages
import os

version = '0.1dev0'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.rst'))

setup(
    name='z3c.formwidget.autocomplete',
    version=version,
    description="AJAX selection widget for Plone",
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Zope3",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Zope",
    ],
    keywords='zope zope3 z3c.form selection widget AJAX autocomplete',
    author='Zach Cashero',
    author_email='zcashero@gmail.com',
    url='http://pypi.python.org/pypi/z3c.formwidget.autocomplete',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c', 'z3c.formwidget'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=[
            'unittest2',
            'z3c.form [test]',
            'zc.buildout',
            'zope.browserpage',
            'zope.publisher',
            'zope.testing',
            'zope.traversing',
        ],
    ),
    install_requires=[
        'setuptools',
        'z3c.formwidget.query == 0.10',
        'z3c.pagelet',
        'zope.interface',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)
