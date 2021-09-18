# Release notes for 0.6.3
  - add support for Hershey Fonts
  - add command line option to set log level

# Release notes for 0.6.2
  - improve ui for windows
  - include translation files in package
  - add option to create empty label

# Release notes for 0.6.1
  - add translation support for ui
  - add german translation

# Release notes for 0.6.0
  - this release is a complete rewrite!
    - much cleaner code for better readability in a more 'pythonic' way
    - logging is now handled via the logging module instead of plain print commands
    - move GUI-code to separate python class with main window
    - remove confusing command line options
    - always create both demo files
    - reduce memory consumption

# Release notes for 0.5.0
  - address comments from users Klartext and TobFleischi at https://de.industryarena.com/heidenhain/forum/gravieren-von-text-in-anderen-sprachen-ohne-cam--83908.html . These changes break compatibility for previous versions
    - add parameter for plunging feed rate
    - use active offset and add incremental changes
    - add command line parameter to generate demo file with cycle 225 for definition of parameters

# Release notes for 0.4.2
  - fixed Warning on implicit conversion of float to integer

# Release notes for 0.4.1
  - update to freetype-py version 2.0 - freetype.dll included

# Release notes for 0.4.0
  - added option to remove empty characters completely or reduce the file size
    by only adding them as labels

# Release notes for 0.3.2
  - fixed error in path generation
  - fixed spelling errors in comments and documentation

# Release notes for 0.3.2
  - code cleanup
  - option to remove empty characters from output

# Release notes for 0.3.1
  - assign all values from the command line
  - setup-script for building stand alone windows binaries

# Release notes for 0.3.0
  - First public release
  - converts font outline to NC code for TNC controls
  - support for 21 character ranges
  - output of demo file
