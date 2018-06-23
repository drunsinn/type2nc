#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="type2nc",
    version="0.3.1",
    author="drunsinn",
    author_email="dr.unsinn@googlemail.com",
    description="convert truetype fonts to klartext nc-code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/drunsinn/type2nc",
    packages=setuptools.find_packages(exclude=['temp', 'tests', 'tests.*', '*.dll']),
    package_data={'': ['demo_pgm_template.H', 'pgm_foot_template.H', 'pgm_head_template.H']},
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=['numpy>=1.6.2', 'scipy>=0.19.0', 'freetype>=1.1', 'argparse>=1.4.0'],
)
