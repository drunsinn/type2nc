# type2nc - convert font outline to Klartext code

![Program and Simulation](/screenshots/screen_1.png?raw=true "Program and Simulation")

type2nc converts the outline of characters in a font file to Klartext
code. The resulting nc program can be used on TNC controls to engrave
text in the corresponding font. The nc program can be used similarly to
the engraving cycle 225 with QS-parameters.

![Path details](/screenshots/screen_3.png?raw=true "Path details")

## Installation

To be able to use type2nc, you need python 3 and the following library's
installed on your system:

  - [numpy](https://www.numpy.org) \>=1.6.2
  - [scipy](https://www.scipy.org) \>=0.19.0
  - [freetype-py](https://github.com/rougier/freetype-py) \>=1.1
  - argparse \>=1.4.0

### Install from Python Packaging Index

To install type2nc and its dependencies from the Python Packaging Index,
first install python3. After a successful setup, type

`pip install type2nc`

on the command line.
To get freetype up and running, you might have to install the binary's
for the library. On Linux and macOS, the library is probably already
installed. For Windows, follow the instructions on  [this github repo](https://github.com/ubawurinna/freetype-windows-binaries).

## Program Usage

 - First, choose a font that has the necessary characters you
   need. Not every font comes with all charakters defined by the
   unicode standard. If a character is not available in your font,
   it will be replaced with a placeholder. Some sources for fonts:

    - <https://fonts.google.com/>
    - <https://www.google.com/get/noto/>
    - <https://fontlibrary.org/>
    - <http://www.fontspace.com/category/open>
    - <https://www.theleagueofmoveabletype.com/>

  - Make sure you have the necessary rights to use the font.

  - Open a command prompt and run python3 type2nc.py or double-click the
    `type2n.py` file

  - Select one or more font files

  - create and select an output folder for the results

  - enter a step size for the conversion. As the outline of a charakter
    consists of curves, these have to be broken down into smaller line
    segments. The smaller the selected step size, the smother the curves
    will be. A smaller step size can also increase the resulting file size
    (several hundred mb).

  - the program will read the font file and convert the outlines to
    Klartext code. This may take some time, depending on the step size
    selected earlier

  - When the program is finished, it will display some statistics about
    the generated code

  - After it is finished, you will find a nc program for every font file
    you selected earlier. There will also be a demo program called
    `type2nc_demo.H` with a usage example.

## NC-Code Usage

The nc program uses these Q parameters:

  - **QS1**: Text to engrave
  - **Q1600**: Z-coordinate of surface
  - **Q1601**: milling depth
  - **Q1602**: safe distance for rapid feed between characters
  - **Q1603**: X-coordinate of the lower left corner of the text
  - **Q1604**: Y-coordinate of the lower left corner of the text
  - **Q1605**: milling feed
  - **Q1606**: approximate height of the engraved text
  - **Q1607**: angle of the text base line

Internally the nc program uses the following parameters:

  - **QL10** to **QL25**: local Q-parameter for internal calculations
  - **QS2** and **QS3**: String-Parameter used as temporary storage

After setting the Q parameters QS1 as well as Q1600 to Q1607, make a
PGM CALL to the generated .H-file with the code for the selected font.

## Known Issues / Problems
### Missing Freetype library
On Windows, when you install freetype-py, the necessary dll files are not
installed automatically. When trying to run type2nc, you get an error message
ending in `RuntimeError: Freetype library not found`. To fix this, follow
the instructions on [this github repo](https://github.com/ubawurinna/freetype-windows-binaries).

### Characters are not included in nc code
To reduce the filesize of the output file, it was chosen to limit the
range of characters to specific sections of the unicode standard:

* BASIC_LATIN: 0x0020 to 0x007E
* C1_CTRL_AND_LATIN1_SUPPLEMENT: 0x0080 to 0x00FF
* IPA_EEXTENTIONS: 0x0250 to 0x02AF
* GREEK_AND_COPTIC_CHARS: 0x0370 to 0x03FF
* CYRILLIC_CHARS: 0x0400 to 0x04FF
* CYRILLIC_SUPPLEMENT_CHARS: 0x0500 to 0x052F
* ARMENIAN_CHARS: 0x0530 to 0x058F
* HEBREW_CHARS: 0x0590 to 0x05FF
* ARABIC_CHARS: 0x0600 to 0x06FF
* SYRIAC_CHARS: 0x0700 to 0x074F
* ARABIC_SUPPLEMENT_CHARS: 0x0750 to 0x077F
* GENERAL_PUNCTUATION: 0x2000 to 0x206F
* ARROW_CHARS: 0x2190 to 0x21FF
* MATHEMATICAL_CHARS: 0x2200 to 0x22FF
* MISC_TECH_CHARS: 0x2300 to 0x23FF
* MISC_SYMBOLS: 0x2600 to 0x26FF
* DINGBATS: 0x2700 to 0x27BF
* CJK_UNIFIED_IDEOGRAPHS_PART1: 0x4E00 to 0x62FF
* CJK_UNIFIED_IDEOGRAPHS_PART2: 0x6300 to 0x77FF
* CJK_UNIFIED_IDEOGRAPHS_PART3: 0x7800 to 0x8CFF
* CJK_UNIFIED_IDEOGRAPHS_PART4: 0x8D00 to 0x9FFF

This results in a total of 23535 characters

If you need more or other characters, let me know and i will add them.
