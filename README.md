# type2nc - convert font outline to Klartext code

![Program and Simulation](/screenshots/screen_1.png?raw=true "Program and Simulation")

type2nc converts the outline of characters in a font file to Klartext
code. The resulting nc program can be used on TNC controls to engrave
text in the corresponding font. The nc program can be used similarly to
the engraving cycle 225 with QS-parameters.

![Path details](/screenshots/screen_3.png?raw=true "Path details")

## Contributors
drunsinn, TobFleischi and Klartext

### Forum
German: [Industry Arena](https://de.industryarena.com/heidenhain/forum/gravieren-von-text-in-anderen-sprachen-ohne-cam--83908.html)

## Requirements
To use the resulting Klartext code on a control, it has to have the following
cycles and functions:

  - cycle 7
  - cycle 10
  - cycle 26
  - INSTR
  - STRLEN
  - STRCOMP
  - FN 9
  - FN 10
  - FN 12
  - FN 18 ID210 NR2
  - FN 18 ID220 NR2 IDX1 and 2
  - FN 18 ID270 NR1 IDX1 and 2

For ease of use it is possible to use cycle 225 for parameter definition. If the
control has cycle 225 you can add use command line option `--use_cycle_def`.

Testing was done on a machine with TNC 620 with software version 817600-03. As
long as the requirements listed above are met, it should work fine.
Support for smaller controls like TNC 128 is untested but the output does not
contain any circular path's.

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

`pip3 install type2nc`

on the command line.
To get freetype up and running, you might have to install the binary's
for the library. On Linux and macOS, the library is probably already
installed. For Windows, follow the instructions on  [this github repo](https://github.com/ubawurinna/freetype-windows-binaries).

## Program Usage

 - First, choose a font that has the necessary characters you
   need. Not every font comes with all characters defined by the
   Unicode standard. If a character is not available in your font,
   it will be replaced with a placeholder. Some sources for fonts:

    - <https://fonts.google.com/>
    - <https://www.google.com/get/noto/>
    - <https://fontlibrary.org/>
    - <http://www.fontspace.com/category/open>
    - <https://www.theleagueofmoveabletype.com/>

  - Make sure you have the necessary rights to use the font.

  - Open a command prompt and run python3 type2nc.py or double-click the
    `type2nc.py` file

  - Select one or more font files

  - create and select an output folder for the results

  - enter a step size for the conversion. As the outline of a character
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

## Command line interface

The program can also be used from the command line. To get information on the
available options, run `python3 type2nc.py -h`
Output:

`usage: type2nc.py [-h] [-i font input file [font input file ...]] [-o output folder]
                  [-s step size] [-r] [-c] [-z]

Create Klartext NC code from font files

optional arguments:
  -h, --help            show this help message and exit
  -i font input file [font input file ...], --input font input file [font input file ...]
                        path of one or more font files
  -o output folder, --out output folder
                        path to the output folder. If not set, use current directory.
  -s step size, --step_size step size
                        step size: between 0.001 (very fine) and 0.2 (very coarse)
  -r, --remove_empty    if set, output won't contain labels for empty chars. overrides -c
  -c, --reduce_empty    if set, output will contain labels for empty characters but no actual data
  -z, --use_cycle_def   if set, demo output will use cycle 225 for definition of parameters`

## NC-Code Usage

The nc program uses the Q parameters also used by cycle 225:

  - **QS500**: Text to engrave
  - **Q203**: Z-coordinate of surface
  - **Q201**: milling depth
  - **Q200**: safe distance for rapid feed between characters
  - **Q206**: plunging feed rate
  - **Q207**: milling feed rate
  - **Q513**: approximate height of the engraved text
  - **Q374**: angle of the text base line

Internally the nc program uses the following parameters:

  - **QL10** to **QL32**: local Q-parameter for internal calculations
  - **QS1** and **QS3**: String-Parameter used as temporary storage

After setting the Q parameters, make a PGM CALL to the generated .H-file with the code for the selected font.

## Known Issues / Problems
### Missing Freetype library
On Windows, when you install freetype-py, the necessary dll files are not
installed automatically. When trying to run type2nc, you get an error message
ending in `RuntimeError: Freetype library not found`. To fix this, follow
the instructions on [this github repo](https://github.com/ubawurinna/freetype-windows-binaries).

### Characters not availibel
To reduce the file size of the output file, it was chosen to limit the
range of characters to specific sections of the Unicode standard:

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
* CJK_UNIFIED_IDEOGRAPHS_PART1: 0x4E00 to 0x9FFF

This results in a total of 23535 characters

If you need more or other characters, let me know and i will add them.

### Windows Installer
There is no All-In-One installer available. If there is enough interest, i may
look into building an installer version.
