#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import cx_Freeze
import os

os.environ['TCL_LIBRARY'] = r'C:\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Python36\tcl\tcl8.6'

with open("README.md", "r") as fh:
    long_description = fh.read()

base = None

executables = [cx_Freeze.Executable("type2nc/type2nc.py", base=base)]

packages = ["idna", "os", "platform", "datetime", "string", "unicodedata",
            "tkinter", "argparse", "numpy", "scipy"]
options = {
    'build_exe': {
        'packages': packages,
    },
}

cx_Freeze.setup(
    name="type2nc",
    author="drunsinn",
    author_email="dr.unsinn@googlemail.com",
    options=options,
    version="0.3.2",
    description="convert truetype fonts to klartext nc-code",
    executables=executables
)
