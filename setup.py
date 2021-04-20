#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setuptools
from type2nc import __version__

setuptools.setup(
    name="type2nc",
    version=__version__,
    author="drunsinn et al.",
    license='MIT',
    author_email="dr.unsinn@googlemail.com",
    description="convert truetype fonts to klartext nc-code",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/drunsinn/type2nc",
    packages=setuptools.find_packages(exclude=['tests',
                                               'tests.*']),
    package_data={'type2nc': ['templates/demo_pgm_template_cycle.H',
                       'templates/demo_pgm_template_conventional.H',
                       'templates/pgm_foot_template.H',
                       'templates/pgm_head_template.H',
                       'locales/en/LC_MESSAGES/*.mo',
                       'locales/de/LC_MESSAGES/*.mo']},
    keywords="cnc klartext font freetype",
    classifiers=(
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=['numpy>=1.6.2',
                      'scipy>=0.19.0',
                      'freetype-py>=1.1',
                      'argparse>=1.4.0'],
    scripts=['type2nc/type2nc.py'],
)
