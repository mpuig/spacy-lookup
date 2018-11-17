#!/usr/bin/env python
# coding: utf8
from __future__ import unicode_literals

from pathlib import Path
from setuptools import setup, find_packages


def setup_package():
    package_name = 'spacy_lookup'
    root = Path(__file__).parent.resolve()

    # Read in package meta from about.py
    about_path = root / package_name / 'about.py'
    with about_path.open('r', encoding='utf8') as f:
        about = {}
        exec(f.read(), about)

    # Get readme
    readme_path = root / 'README.rst'
    with readme_path.open('r', encoding='utf8') as f:
        readme = f.read()

    setup(
        name=package_name,
        description=about['__summary__'],
        long_description=readme,
        author=about['__author__'],
        author_email=about['__email__'],
        url=about['__url__'],
        version=about['__version__'],
        license=about['__license__'],
        packages=find_packages(),
        install_requires=[
            'spacy>=2.0.16,<3.0.0',
            'flashtext>=2.7'],
        zip_safe=False,
        tests_require=['pytest']
    )


if __name__ == '__main__':
    setup_package()
