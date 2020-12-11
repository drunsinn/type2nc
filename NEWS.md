# Reselase notes for 0.5.0
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
