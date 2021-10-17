#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: drunsinn, TobFleischi, Klartext and GuggiJr
'''

import datetime
import logging
import argparse
import pathlib
import math
import string
import freetype
import numpy as np
from scipy.special import binom
from HersheyFonts import HersheyFonts

class Point():
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    
    def __str__(self):
        return "X:{:+0.4f} Y:{:+0.4f}".format(self.x, self.y)
    
    def scaled_str(self, scale_factor=1.0):
        return "X{:+0.4f} Y{:+0.4f}".format(self.x * scale_factor, self.y * scale_factor)

    def scaled_offset_str(self, scale_factor=1.0, offset_x=0.0, offset_y=0.0):
        return "X{:+0.4f} Y{:+0.4f}".format((self.x * scale_factor) + offset_x,
                                             (self.y * scale_factor) + offset_y)

class Type2NC(object):

    def __init__(self, output_folder, target_height, step_size, unicode_numbers=None, create_empty_labels=False, only_numeric=False):
        self._log = logging.getLogger("Type2NC")
        self.__output_folder = output_folder.resolve(strict=True)
        self.__target_height = target_height
        self.__step_size = step_size
        self.__char_size_pt = 10
        self.__char_size_dpi = 140
        self.__only_numeric = only_numeric

        self.__characters = list()
        if unicode_numbers is None and self.__only_numeric is False:
            self.__characters.extend(list(range(0x0020, 0x007E + 1))) # BASIC_LATIN
            self.__characters.extend(list(range(0x0080, 0x00FF + 1))) # C1_CTRL_AND_LATIN1_SUPPLEMENT
            self.__characters.extend(list(range(0x2000, 0x206F + 1))) # GENERAL_PUNCTUATION
            self.__characters.extend(list(range(0x0250, 0x02AF + 1))) # IPA_EEXTENTIONS
            self.__characters.extend(list(range(0x0370, 0x03FF + 1))) # GREEK_AND_COPTIC_CHARS
            self.__characters.extend(list(range(0x0400, 0x04FF + 1))) # CYRILLIC_CHARS
            self.__characters.extend(list(range(0x0500, 0x052F + 1))) # CYRILLIC_SUPPLEMENT_CHARS
            self.__characters.extend(list(range(0x0530, 0x058F + 1))) # ARMENIAN_CHARS
            self.__characters.extend(list(range(0x0590, 0x05FF + 1))) # HEBREW_CHARS
            self.__characters.extend(list(range(0x0600, 0x06FF + 1))) # ARABIC_CHARS
            self.__characters.extend(list(range(0x0700, 0x074F + 1))) # SYRIAC_CHARS
            self.__characters.extend(list(range(0x0750, 0x077F + 1))) # ARABIC_SUPPLEMENT_CHARS
            self.__characters.extend(list(range(0x2190, 0x21FF + 1))) # ARROW_CHARS
            self.__characters.extend(list(range(0x2200, 0x22FF + 1))) # MATHEMATICAL_CHARS
            self.__characters.extend(list(range(0x2300, 0x23FF + 1))) # MISC_TECH_CHARS
            self.__characters.extend(list(range(0x2600, 0x26FF + 1))) # MISC_SYMBOLS
            self.__characters.extend(list(range(0x2700, 0x27BF + 1))) # DINGBATS
            self.__characters.extend(list(range(0x4E00, 0x9FFF + 1))) # CJK_UNIFIED_IDEOGRAPHS_PART
        elif self.__only_numeric is True:
            self.__characters.extend(list(range(0x0020, 0x007E + 1))) # BASIC_LATIN
        else:
            self.__characters.extend(unicode_numbers)
        
        self.__create_empty_labels = create_empty_labels
        
        self._log.debug("using folder '%s', step size '%f'", self.__output_folder, self.__step_size)
    
    def convert_freetype(self, font_file):
        self._log.debug("running for font file '%s' for %d characters", font_file.resolve(strict=True), len(self.__characters))

        font_face = freetype.Face(str(font_file.resolve(strict=True)))
        self._log.info("Font: %s, Style: %s, Format: %s", font_face.family_name.decode("utf-8"), font_face.style_name.decode("utf-8"), font_face.get_format().decode("utf-8"))
        #font_face.set_char_size(height=self.__char_size)
        try:
            font_face.set_char_size(height=self.__char_size_pt * self.__char_size_dpi, hres=self.__char_size_dpi, vres=self.__char_size_dpi)
        except freetype.ft_errors.FT_Exception as e:
            self._log.error("Error while setting size for font %s %s : %s", font_face.family_name.decode("utf-8"), font_face.style_name.decode("utf-8"), e)
            return        

        self._log.info("Font BBox (min:max) X:(%d:%d) Y:(%d:%d)", font_face.bbox.xMax, font_face.bbox.xMin, font_face.bbox.yMax, font_face.bbox.yMin)
        scale_factor = self.__target_height / (abs(font_face.bbox.yMax) + abs(font_face.bbox.yMin))
        self._log.info("set scaling factor to %f", scale_factor)

        nc_file_name = font_file.name.replace(font_file.suffix, '.H')
        nc_file_name = nc_file_name.replace(' ', '_')
        nc_file_path = self.__output_folder.joinpath(nc_file_name)

        with open(nc_file_path, 'w') as ncfp:
            ncfp.write("BEGIN PGM {0:s} MM\n".format(font_file.name.replace(font_file.suffix, '').upper()))
                    
            ncfp.write(";\n; Font PGM generated by type2nc\n")
            ncfp.write("; {0:s} - {1:s}\n".format(font_face.family_name.decode("utf-8"), font_face.style_name.decode("utf-8")))
            ncfp.write("; Generated: {:%Y-%m-%d %H:%M:%S}\n".format(datetime.datetime.today()))
            ncfp.write("; Number of characters: {0:d}\n;\n".format(len(self.__characters)))

            if self.__only_numeric:
                template_path = pathlib.Path.cwd().joinpath("templates", "pgm_head_template_numeric.H")
            else:
                template_path = pathlib.Path.cwd().joinpath("templates", "pgm_head_template.H")

            with open(template_path) as template_file:
                ncfp.writelines(template_file)

            for char_code in self.__characters:
                char_index = font_face.get_char_index(char_code)
                if char_index > 0:
                    self._log.debug("character '%s' available at index %d", chr(char_code), char_index)

                    contour_paths = self._path_from_charcode_freetype(font_face, char_code)
                    x_advance = self._xadvance_from_charcode_freetype(font_face, char_code)

                    if contour_paths is None:
                        if self.__create_empty_labels:
                            self._log.info("character '%s' was selected but is not available, add empty label", chr(char_code))
                            ncfp.writelines(self._create_empty_font_label(chr(char_code), x_advance=0))
                        else:
                            self._log.info("character '%s' at index %d could not be loaded, skip. Error: %s", chr(char_code), char_index)
                    else:
                        ncfp.writelines(self._creat_font_label(chr(char_code), contour_paths, x_advance, scale_factor))
                    
                else:
                    if self.__create_empty_labels:
                        self._log.debug("character '%s' was selected but is not available, add empty label", chr(char_code))
                        ncfp.writelines(self._create_empty_font_label(chr(char_code), x_advance=0))
                    else:
                        self._log.debug("character '%s' was selected but is not available, skipping", chr(char_code))

            with open(pathlib.Path.cwd().joinpath("templates", "pgm_foot_template.H")) as template_file:
                    ncfp.writelines(template_file)

            ncfp.write("END PGM {0:s} MM".format(font_file.name.replace(font_file.suffix, '').upper()))

        self._log.info("finished writing %s", nc_file_name)

    def _path_from_charcode_freetype(self, font_face, char_code):

        try:
            font_face.load_char(char_code)
        except freetype.ft_errors.FT_Exception as e:
            char_index = font_face.get_char_index(char_code)
            self._log.error("character '%s' at index %d could not be loaded. Error: %s", chr(char_code), char_index, e)
            return None

        c_glyph_slot = font_face.glyph

        contour_paths = list()

        self._log.debug("character '%s' advance X:%d Y:%d linear horizontal advance:%d", char_code, c_glyph_slot.advance.x, c_glyph_slot.advance.y, c_glyph_slot.linearHoriAdvance)

        if c_glyph_slot.outline.n_points > 1:
            self._log.debug("character '%s' has %d points in %d contour(s) with %d tags", char_code, c_glyph_slot.outline.n_points, c_glyph_slot.outline.n_contours, len(c_glyph_slot.outline.tags))
                        
            start, end = 0, 0

            for i in range(0, c_glyph_slot.outline.n_contours):
                path_points = list()
                contour_segments = list()
                end = c_glyph_slot.outline.contours[i]
                            
                # slice lists of points and tags according to length of contour
                contour_tags = c_glyph_slot.outline.tags[start:end+1]
                contour_tags.append(c_glyph_slot.outline.tags[0])
                contour_points = c_glyph_slot.outline.points[start:end+1]
                contour_points.append(c_glyph_slot.outline.points[0])

                # add first point in list to segment to start things of
                contour_segments.append([contour_points[0], ])

                # split the list of all the points in separate segments
                # with the right amount for each contour type
                for j in range(1, len(contour_points)): # skip first point as it is already in the list
                    contour_segments[-1].append(contour_points[j])
                    if contour_tags[j] & (1 << 0) and j < (len(contour_points) - 1):
                        contour_segments.append([contour_points[j], ])

                # finally, check each segment for the number of points it contains.
                # if only two the segmet is a line so we can just add the end point to our list
                # if there are more than two points in the segment we have to step along the bezier curve
                for segment in contour_segments:
                    if len(segment) == 2:  # line segment, add endpoint to list
                        path_points.append(Point(x=segment[0][0], y=segment[0][1]))
                    else:  # bezier curve, split into segments an add them to list
                        num_points = int(1.0 / self.__step_size)      
                        for t in np.linspace(0.0, 1.0, num_points, endpoint=True):
                            path_points.append(self._point_on_curve(segment[:-1], t))
                            
                # close path by addind the first point a second time
                path_points.append(Point(x=contour_segments[0][0][0], y=contour_segments[0][0][1]))

                start = end + 1
                contour_paths.append(path_points)
                self._log.debug("created %d points for character contour %d",  len(path_points), i)

            self._log.debug("created %d paths for character", len(contour_paths))
                        
        else:
            self._log.debug("character '%s' is empty, skipping", char_code)

        return contour_paths

    def _xadvance_from_charcode_freetype(self, font_face, char_code):
        font_face.load_char(char_code)
        c_glyph_slot = font_face.glyph
        if c_glyph_slot.advance.x > 0:
            x_advance = c_glyph_slot.advance.x
        else:
            self._log.debug("character '%s' has no advance x value, use glyph width %d", char_code, c_glyph_slot.metrics.width)
            x_advance = c_glyph_slot.metrics.width
        return x_advance
    
    def convert_hershey(self, font_file):
        hshf = HersheyFonts()
        if isinstance(font_file, pathlib.Path):
            self._log.debug("running for hershey font file '%s' for %d characters", font_file.resolve(strict=True), len(self.__characters))
            hshf.load_font_file(font_file)
            nc_file_name = font_file.name.replace(font_file.suffix, '')
        else:
            self._log.debug("running for hershey default font '%s' for %d characters", font_file, len(self.__characters))
            hshf.load_default_font(font_file)
            nc_file_name = font_file

        hshf.normalize_rendering(self.__target_height * 0.8)

        nc_file_name = nc_file_name.replace(' ', '_')
        nc_file_path = self.__output_folder.joinpath(nc_file_name + '.H')

        scale_factor = 1.0

        with open(nc_file_path, 'w') as ncfp:
            ncfp.write("BEGIN PGM {0:s} MM\n".format(nc_file_name.upper()))
                    
            ncfp.write(";\n; Font PGM generated by type2nc\n")
            ncfp.write("; Hershey Font File: {0:s}\n".format(nc_file_name))
            ncfp.write("; Generated: {:%Y-%m-%d %H:%M:%S}\n".format(datetime.datetime.today()))
            ncfp.write("; Number of characters: {0:d}\n;\n".format(len(self.__characters)))

            if self.__only_numeric:
                template_path = pathlib.Path.cwd().joinpath("templates", "pgm_head_template_numeric.H")
            else:
                template_path = pathlib.Path.cwd().joinpath("templates", "pgm_head_template.H")

            with open(template_path) as template_file:
                ncfp.writelines(template_file)

            for char_code in self.__characters:
                contour_paths = self._path_from_charcode_hershey(hshf, chr(char_code))
                x_advance = self._xadvance_from_charcode_hershey(hshf, chr(char_code))

                if len(contour_paths) > 0:
                    ncfp.writelines(self._creat_font_label(chr(char_code), contour_paths, x_advance, scale_factor=scale_factor))
                else:
                    if self.__create_empty_labels:
                        self._log.debug("character '%s' was selected but is not available, add empty label", chr(char_code))
                        ncfp.writelines(self._create_empty_font_label(chr(char_code), x_advance=0))
                    else:
                        self._log.debug("character '%s' was selected but is not available, skipping", chr(char_code))

            with open(pathlib.Path.cwd().joinpath("templates", "pgm_foot_template.H")) as template_file:
                    ncfp.writelines(template_file)

            ncfp.write("END PGM {0:s} MM".format(nc_file_name.upper()))

    def _path_from_charcode_hershey(self, hshf, char_code):
        contour_paths = list()
        count = 0
        x_advance = None
        for glyph in hshf.glyphs_for_text(char_code):
            if count > 0:
                raise Exception("recived unexpected number of glyphs {:d} for {:s}".format(count, char_code))
            count += 1

            for stroke in glyph.strokes:
                path_points = list()
                for c_pair in stroke:
                    x_coor = c_pair[0] - glyph.left_offset
                    y_coor = -1 * c_pair[1]
                    path_points.append(Point(x=x_coor, y=y_coor))
                contour_paths.append(path_points)
            self._log.debug("created %d paths for character", len(contour_paths))
        return contour_paths

    def _xadvance_from_charcode_hershey(self, hshf, char_code):
        glyph_generator = hshf.glyphs_for_text(char_code)
        glyph = next(glyph_generator, None)
        if glyph is None:
            self._log.debug("character '%s' is not availible for this font", char_code)
            return None
        x_advance = glyph.char_width + 1.0
        self._log.debug("character '%s' advance X:%d", char_code, x_advance)
        return x_advance

    def _point_on_curve(self, point_list, distance_factor):
        """Get x and y coordinate for point along a bezier curve relative to
        the length of the curve.

        Keyword arguments:
        point_list -- points defining the bezier curve
        distance_factor -- relative distance
        """
        if distance_factor < 0.0 or distance_factor > 1.0:
            raise ValueError("factor has to be a value between 0 and 1")
        n = len(point_list) - 1
        c_t_x = 0
        c_t_y = 0
        for i, point in enumerate(point_list):
            b_i_n = binom(n, i) * (distance_factor ** i) * np.power((1 - distance_factor), (n - i))
            c_t_x += b_i_n * point[0]
            c_t_y += b_i_n * point[1]
        return Point(x=c_t_x, y=c_t_y)
    
    def _creat_font_label(self, char_str, contour_paths, x_advance, scale_factor):
        self._log.debug("create label for char %s", char_str)
        char_lines = list()
        label_name = self._translate_label_name(char_str)
        self._log.debug("writing label for character '%s': %d %s", char_str, ord(char_str), label_name)

        if char_str in string.ascii_letters + string.digits:
            char_lines.append("* -   {0:s}\n".format(char_str))

        if label_name is not None:
            char_lines.append("LBL \"{0:s}\"\n".format(label_name))
            char_lines.append("* -   Unicode Hex:0x{0:04x} : {1:s}\n".format(ord(char_str), label_name))
        else:
            char_lines.append("* -   Unicode Hex:0x{0:04x}\n".format(ord(char_str)))
        char_lines.append("LBL \"0x{0:04x}\"\n".format(ord(char_str)))
        
        for path in contour_paths:
            char_lines.append("L {0:s} FMAX\n".format(path[0].scaled_str(scale_factor)))
            char_lines.append("L Z+QL15 F+Q206\n")
            for point in path[1:]:
                char_lines.append("L {0:s} F+Q207\n".format(point.scaled_str(scale_factor)))
            char_lines.append("L IZ+0.01 F+Q206\n")
            char_lines.append("L Z+Q204 FMAX\n")
        char_lines.append("L Z+QL32 FMAX\n")

        if label_name is not None: char_lines.append("LBL \"{0:s}_X-Advance\"\n".format(label_name))
        char_lines.append("LBL \"0x{0:04x}_X-Advance\"\n".format(ord(char_str)))
        char_lines.append("QL20 = {0:+f} ; X-Advance\n".format(x_advance * scale_factor))
        char_lines.append("LBL 0\n;\n")
        self._log.debug("created %d lines for char %s", len(char_lines), char_str)
        return char_lines

    def _creat_numeric_font_label(self, char_str, contour_paths, x_advance, scale_factor):
        self._log.debug("create label for char %s", char_str)
        char_lines = list()
        self._log.debug("writing label for character '%s': %d", char_str, ord(char_str))
        char_lines.append("* - Unicode Hex:0x{0:04x} : {1:s}\n".format(ord(char_str), self._translate_label_name(char_str)))
        char_lines.append("LBL {0:d}\n".format(ord(char_str)))
        
        for path in contour_paths:
            char_lines.append("L {0:s} FMAX\n".format(path[0].scaled_str(scale_factor)))
            char_lines.append("L Z+QL15 F+Q206\n")
            for point in path[1:]:
                char_lines.append("L {0:s} F+Q207\n".format(point.scaled_str(scale_factor)))
            char_lines.append("L IZ+0.01 F+Q206\n")
            char_lines.append("L Z+Q204 FMAX\n")
        char_lines.append("L Z+QL32 FMAX\n")

        char_lines.append("QL20 = {0:+f} ; X-Advance\n".format(x_advance * scale_factor))
        char_lines.append("LBL 0\n;\n")
        self._log.debug("created %d lines for char %s", len(char_lines), char_str)
        return char_lines

    def _create_empty_font_label(self, char_str, x_advance):
        self._log.debug("created label for empty char %s", char_str)
        char_lines = list()
        char_lines.append("* -   Unicode Hex:0x{0:04x}\n".format(ord(char_str)))
        char_lines.append("LBL \"0x{0:04x}\"\n".format(ord(char_str)))
        char_lines.append("LBL \"0x{0:04x}_X-Advance\"\n".format(ord(char_str)))
        char_lines.append("QL20 = {0:+f} ; X-Advance\n".format(x_advance))
        char_lines.append("LBL 0\n;\n")
        return char_lines

    def _translate_label_name(self, char_str):
        label_map = {
            '!': 'exclamation_mark',
            '\'': 'apostrophe',
            '(': 'opening_parenthese',
            ')': 'closing_parenthese',
            '*': 'asterisk',
            '+': 'plus',
            '/': 'slash',
            ':': 'colon',
            ';': 'semicolon',
            '<': 'less_than',
            '=': 'equal',
            '>': 'greater_than',
            '?': 'question_mark',
            '@': 'at',
            '[': 'opening_square_brackets',
            '\\': 'backslash',
            ']': 'closing_square_brackets',
            '^': 'caret',
            '"': 'quotation_marks',
            '`': 'prime',
            '{': 'opening_braces',
            '|': 'pipe',
            '}': 'closing_braces',
            '~': 'tilde',
            'ä': 'ae',
            'ö': 'oe',
            'ü': 'ue',
            'Ä': 'AE',
            'Ö': 'OE',
            'Ü': 'UE',
            ' ': 'space'
        }
        if char_str in label_map.keys():
            label_name = label_map[char_str]
        elif char_str in string.ascii_letters + string.digits + string.punctuation:
            label_name = char_str
        else:
            label_name = None  # could not identify character
        return label_name
    
    def generate_demo_files(self, font_file_list):
        self._log.debug("create demo files")
        filler = ""
        current_y = 5
        for font_file in font_file_list:
            nc_file_name = font_file.name.replace(font_file.suffix, '.H')
            nc_file_name = nc_file_name.replace(' ', '_')

            filler += "L X+5 Y+%d Z+100 R0 FMAX\n" % current_y
            filler += "CALL PGM %s\n;\n" % nc_file_name
            current_y += self.__target_height + 5
        filler = filler.rstrip("\n")

        block_heigth = current_y + 2 * self.__target_height
            
        with open(pathlib.Path.cwd().joinpath("templates", "demo_pgm_template_conventional.H")) as template_file:
            with open(self.__output_folder.joinpath("type2nc_demo_conventional.H"), 'w') as output_file:
                demo_file_content = template_file.read()
                output_file.write(demo_file_content.format(block_heigth, filler))
        self._log.debug("demo file for conventional calling written successfully")
    
        with open(pathlib.Path.cwd().joinpath("templates", "demo_pgm_template_cycle.H")) as template_file:
            with open(self.__output_folder.joinpath("type2nc_demo_cycle.H"), 'w') as output_file:
                demo_file_content = template_file.read()
                output_file.write(demo_file_content.format(block_heigth, filler))
        self._log.debug("demo file for cycle based calling written successfully")

    def convert_to_static(self, font_file, message):

        font_name = font_file.name.replace(font_file.suffix, '')

        if len(message) >= 8:
            cut_length = 8
        else:
            cut_length = len(message)

        nc_file_name = "static_" + message[:cut_length] + "_" + font_name
        nc_file_name = nc_file_name.replace(" ", "_")
        nc_file_name = nc_file_name.upper()

        output_file = self.__output_folder.joinpath(nc_file_name + ".H")

        current_x = 0.0

        if font_file.suffix.lower() in ".jhf":
            fnt = HersheyFonts()
            fnt.load_font_file(font_file)
            fnt.normalize_rendering(self.__target_height * 0.8)
            scale_factor = 1.0
            font_title = "; Hershey Font File: {0:s}\n".format(font_name)
        else:
            fnt = freetype.Face(str(font_file.resolve(strict=True)))
            fnt.set_char_size(height=self.__char_size_pt * self.__char_size_dpi,
                              hres=self.__char_size_dpi, vres=self.__char_size_dpi)
            scale_factor = self.__target_height / (abs(fnt.bbox.yMax) + abs(fnt.bbox.yMin))
            font_title = "; {0:s} - {1:s}\n".format(fnt.family_name.decode("utf-8"), fnt.style_name.decode("utf-8"))
                
        with open(output_file, "w") as output_file:
            output_file.write("BEGIN PGM {0:s} MM\n".format(nc_file_name))
            output_file.write("BLK FORM 0.1 Z X+0 Y+0 Z-20\n")
            output_file.write("BLK FORM 0.2 X+200 Y+20 Z+0\n")

            output_file.write(";\n")

            output_file.write(";\n; static Font PGM generated by type2nc\n")
            output_file.write(font_title)
            output_file.write("; Generated: {:%Y-%m-%d %H:%M:%S}\n".format(datetime.datetime.today()))
            output_file.write("; Message: {:s}\n;\n".format(message))

            output_file.write("Q201 = -0.5 ; Depth\n")
            output_file.write("Q204 = 2 ; Safe Height\n")
            output_file.write("Q206 = 300 ; Plunge Feed Rate\n")
            output_file.write("Q207 = 500 ; milling feed rate\n;\n")

            output_file.write('TOOL CALL "GRAVIER" Z S5000 F500\n')
            output_file.write("M3\n;\n")

            for character in message:
                output_file.write("* - {:s}\n".format(character))

                if font_file.suffix.lower() in ".jhf":
                    contour_paths = self._path_from_charcode_hershey(fnt, character)
                    x_advance = self._xadvance_from_charcode_hershey(fnt, character)
                else:
                    contour_paths = self._path_from_charcode_freetype(fnt, character)
                    x_advance = self._xadvance_from_charcode_freetype(fnt, character)
                
                for path in contour_paths:
                    output_file.write("L {0:s} FMAX\n".format(path[0].scaled_offset_str(scale_factor=scale_factor,
                                                                                        offset_x=current_x)))
                    output_file.write("L Z+Q201 F+Q206\n")
                    for point in path[1:]:
                        output_file.write("L {0:s} F+Q207\n".format(point.scaled_offset_str(scale_factor=scale_factor,
                                                                                        offset_x=current_x)))
                    output_file.write("L IZ+0.01 F+Q206\n")
                    output_file.write("L Z+Q204 FMAX\n")
                output_file.write(";\n;\n")
                current_x += x_advance * scale_factor

            output_file.write("END PGM {0:s} MM\n".format(nc_file_name))


class Type2NC_UI:
    def __init__(self, root):
        self._log = logging.getLogger("Type2NCUI")
        self._log.debug("start building tk ui")

        for lang in ['en', 'de']:
            lang_translations = gettext.translation('messages', localedir='locales', languages=[lang])
            lang_translations.install()
        
        self.gt_ = lang_translations.gettext

        self._window_root = root
        root.title("Type2NC UI")
        width=670
        height=300
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self._window_root.geometry(alignstr)
        self._window_root.resizable(width=False, height=False)

        ft = tkFont.Font(family='Times', size=12)

        current_y = 20
        delta_y = 40
        component_height = 30

        self.btn_select_font = tk.Button(self._window_root)
        self.btn_select_font["font"] = ft
        self.btn_select_font["justify"] = "center"
        self.btn_select_font["text"] = self.gt_("Select Font File")
        self.btn_select_font.place(x=20, y=current_y, width=160, height=component_height)
        self.btn_select_font["command"] = self.btn_select_font_command

        self.lbl_font_filename = tk.Label(self._window_root)
        self.lbl_font_filename["font"] = ft
        self.lbl_font_filename["justify"] = "center"
        self.lbl_font_filename["text"] = " "
        self.lbl_font_filename["anchor"] = "w"
        self.lbl_font_filename.place(x=200, y=current_y, width=180, height=component_height)
        current_y += delta_y

        self.include_hershey = tk.IntVar()
        self.chk_hershey = tk.Checkbutton(self._window_root)
        self.chk_hershey["font"] = ft
        self.chk_hershey["justify"] = "left"
        self.chk_hershey["text"] = self.gt_("Include Default Hershey Fonts")
        self.chk_hershey["anchor"] = "w"
        self.chk_hershey.place(x=20, y=current_y, width=220, height=component_height)
        self.chk_hershey["onvalue"] = 1
        self.chk_hershey["offvalue"] = 0
        self.chk_hershey["variable"] = self.include_hershey
        self.chk_hershey.deselect()
        current_y += delta_y

        self.btn_select_folder = tk.Button(self._window_root)
        self.btn_select_folder["font"] = ft
        self.btn_select_folder["justify"] = "center"
        self.btn_select_folder["text"] = self.gt_("Select Destination Folder")
        self.btn_select_folder.place(x=20, y=current_y, width=160, height=component_height)
        self.btn_select_folder["command"] = self.btn_select_folder_command

        self.lbl_output_path = tk.Label(self._window_root)
        self.lbl_output_path["font"] = ft
        self.lbl_output_path["justify"] = "center"
        self.lbl_output_path["text"] = " "
        self.lbl_output_path["anchor"] = "w"
        self.lbl_output_path.place(x=200, y=current_y, width=180, height=component_height)
        current_y += delta_y

        self.btn_select_step = tk.Button(self._window_root)
        self.btn_select_step["font"] = ft
        self.btn_select_step["justify"] = "center"
        self.btn_select_step["text"] = self.gt_("Select Step Size")
        self.btn_select_step.place(x=20, y=current_y, width=160, height=component_height)
        self.btn_select_step["command"] = self.btn_select_step_command

        self.lbl_step_size = tk.Label(self._window_root)
        self.lbl_step_size["font"] = ft
        self.lbl_step_size["justify"] = "center"
        self.lbl_step_size["text"] = " "
        self.lbl_step_size["anchor"] = "w"
        self.lbl_step_size.place(x=200, y=current_y, width=180, height=component_height)
        current_y += delta_y

        self.gen_demo_files = tk.IntVar()
        self.chk_generate_demos = tk.Checkbutton(self._window_root)
        self.chk_generate_demos["font"] = ft
        self.chk_generate_demos["justify"] = "left"
        self.chk_generate_demos["text"] = self.gt_("Create Demo Files")
        self.chk_generate_demos["anchor"] = "w"
        self.chk_generate_demos.place(x=20, y=current_y, width=220, height=component_height)
        self.chk_generate_demos["onvalue"] = 1
        self.chk_generate_demos["offvalue"] = 0
        self.chk_generate_demos["variable"] = self.gen_demo_files
        self.chk_generate_demos.select()
        current_y += delta_y

        self.include_empty_lbl = tk.IntVar()
        self.chk_empty_lbl = tk.Checkbutton(self._window_root)
        self.chk_empty_lbl["font"] = ft
        self.chk_empty_lbl["justify"] = "left"
        self.chk_empty_lbl["text"] = self.gt_("Include Empty Label")
        self.chk_empty_lbl["anchor"] = "w"
        self.chk_empty_lbl.place(x=20, y=current_y, width=220, height=component_height)
        self.chk_empty_lbl["onvalue"] = 1
        self.chk_empty_lbl["offvalue"] = 0
        self.chk_empty_lbl["variable"] = self.include_empty_lbl
        self.chk_empty_lbl.select()
        current_y += delta_y

        self.btn_generate_nc = tk.Button(self._window_root)
        self.btn_generate_nc["font"] = ft
        self.btn_generate_nc["justify"] = "center"
        self.btn_generate_nc["text"] = self.gt_("Generate")
        self.btn_generate_nc.place(x=140, y=current_y, width=150, height=component_height)
        self.btn_generate_nc["command"] = self.btn_generate_nc_command
        current_y += delta_y

        self.pb_progress = ttk.Progressbar(self._window_root)
        self.pb_progress["orient"] = tk.HORIZONTAL
        self.pb_progress["length"] = 100
        self.pb_progress.place(x=115, y=current_y, width=200, height=component_height)
        self.pb_progress["mode"] = 'determinate'
        self.pb_progress['value'] = 0
        current_y = 20

        self.select_basics = tk.IntVar()
        self.chk_select_basic = tk.Checkbutton(self._window_root)
        self.chk_select_basic["font"] = ft
        self.chk_select_basic["justify"] = "left"
        self.chk_select_basic["text"] = self.gt_("ASCII 0x20-0x7E and Latin1 0x80-0xFF")
        self.chk_select_basic["anchor"] = "w"
        self.chk_select_basic.place(x=390, y=current_y, width=260, height=component_height)
        self.chk_select_basic["onvalue"] = 1
        self.chk_select_basic["offvalue"] = 0
        self.chk_select_basic["variable"] = self.select_basics
        self.chk_select_basic.select()
        current_y += delta_y

        self.select_punctuation = tk.IntVar()
        self.chk_select_punctuation = tk.Checkbutton(self._window_root)
        self.chk_select_punctuation["font"] = ft
        self.chk_select_punctuation["justify"] = "left"
        self.chk_select_punctuation["text"] = self.gt_("General Punctuation 0x2000-0x206F")
        self.chk_select_punctuation["anchor"] = "w"
        self.chk_select_punctuation.place(x=390, y=current_y, width=260, height=component_height)
        self.chk_select_punctuation["onvalue"] = 1
        self.chk_select_punctuation["offvalue"] = 0
        self.chk_select_punctuation["variable"] = self.select_punctuation
        self.chk_select_punctuation.select()
        current_y += delta_y

        self.select_ipa = tk.IntVar()
        self.chk_select_ipa = tk.Checkbutton(self._window_root)
        self.chk_select_ipa["font"] = ft
        self.chk_select_ipa["justify"] = "left"
        self.chk_select_ipa["text"] = self.gt_("IPA Extension 0x0250-0x02AF")
        self.chk_select_ipa["anchor"] = "w"
        self.chk_select_ipa.place(x=390, y=current_y, width=260, height=component_height)
        self.chk_select_ipa["onvalue"] = 1
        self.chk_select_ipa["offvalue"] = 0
        self.chk_select_ipa["variable"] = self.select_ipa
        self.chk_select_ipa.select()
        current_y += delta_y

        self.select_symbols= tk.IntVar()
        self.chk_select_symbols = tk.Checkbutton(self._window_root)
        self.chk_select_symbols["font"] = ft
        self.chk_select_symbols["justify"] = "left"
        self.chk_select_symbols["text"] = self.gt_("Symbols 0x2190-0x23FF & 0x2600-0x27BF")
        self.chk_select_symbols["anchor"] = "w"
        self.chk_select_symbols.place(x=390, y=current_y, width=260, height=component_height)
        self.chk_select_symbols["onvalue"] = 1
        self.chk_select_symbols["offvalue"] = 0
        self.chk_select_symbols["variable"] = self.select_symbols
        self.chk_select_symbols.select()
        current_y += delta_y

        self.select_add_lang = tk.IntVar()
        self.chk_select_lang = tk.Checkbutton(self._window_root)
        self.chk_select_lang["font"] = ft
        self.chk_select_lang["justify"] = "left"
        self.chk_select_lang["text"] = self.gt_("Lang 0x0370-0x077F & 0x4E00-0x9FFF")
        self.chk_select_lang["anchor"] = "w"
        self.chk_select_lang.place(x=390, y=current_y, width=260, height=component_height)
        self.chk_select_lang["onvalue"] = 1
        self.chk_select_lang["offvalue"] = 0
        self.chk_select_lang["variable"] = self.select_add_lang
        self.chk_select_lang.select()
        current_y += delta_y

        self._log.debug("ui ready")

        self.selected_font_files = list()
        self.output_path = None
        self.step_size = None

    def btn_select_font_command(self):
        self._log.debug("select font button pressed")
        
        file_types = [('Font', '*.ttf *.tte *.ttc *.otf *.dfont *.pfb'), ('Hershey Font', '*.jhf')]
        font_file_list = tkfd.askopenfilename(parent=self._window_root, title=self.gt_("Select Font File"), filetypes=file_types, multiple=1)
        for path in font_file_list:
            self.selected_font_files.append(pathlib.Path(path))

        if len(self.selected_font_files) == 1:
            self.lbl_font_filename["text"] = str(self.selected_font_files[0].name)
            self._log.debug("No font file selected")
        else:
            self.lbl_font_filename["text"] = self.gt_("%d files selected") % len(self.selected_font_files)
            self._log.debug("Add %d fonts to list: %s", len(font_file_list), font_file_list)

    def btn_select_folder_command(self):
        self._log.debug("select output folder button pressed")
        
        selected_folder = tkfd.askdirectory(parent=self._window_root, title=self.gt_("Select Destination Folder"))
        self.output_path = pathlib.Path(selected_folder)

        if not self.output_path.is_dir():
            self.output_path = None
            self.lbl_output_path["text"] = self.gt_("No folder selected")
            self._log.debug("No folder selected")
        else:
            self.lbl_output_path["text"] = self.output_path.name
            self._log.debug("Output folder set to %s", self.output_path)

    def btn_select_step_command(self):
        self._log.debug("select step size button pressed")
        
        selected_step = tksd.askfloat(parent=self._window_root, title=self.gt_("Step Size"), prompt=self.gt_("Step Size between 0.001 (very fine) and 0.2 (very coarse) for converting Splines"), initialvalue=0.05, minvalue=0.001, maxvalue=0.2)
        if selected_step is None:
            self.step_size = None
            self.lbl_step_size["text"] = self.gt_("No step size selected")
            self._log.debug("No step size selected")
        else:
            self.step_size = selected_step
            self.lbl_step_size["text"] = "%f" % self.step_size
            self._log.debug("step size set to %f", self.step_size)

    def btn_generate_nc_command(self):
        self._log.debug("generate nc files button pressed")
        
        if len(self.selected_font_files) == 0 and self.include_hershey.get() == 0:
            tkmb.showwarning(parent=self._window_root, title=self.gt_("Missing parameter"), message=self.gt_("No font files selected"))
            self._log.debug("list of selected font files is empty!")
            return
        if self.output_path is None:
            tkmb.showwarning(parent=self._window_root, title=self.gt_("Missing parameter"), message=self.gt_("No output folder selected"))
            self._log.debug("no output path selected!")
            return
        if self.step_size is None:
            tkmb.showwarning(parent=self._window_root, title=self.gt_("Missing parameter"), message=self.gt_("No step size selected"))
            self._log.debug("no step size selected selected!")
            return
        
        character_list = list()
        if self.select_basics.get() > 0:
            character_list.extend(list(range(0x0020, 0x007E + 1))) # BASIC_LATIN
            character_list.extend(list(range(0x0080, 0x00FF + 1))) # C1_CTRL_AND_LATIN1_SUPPLEMENT

        if self.select_punctuation.get() > 0:
            character_list.extend(list(range(0x2000, 0x206F + 1))) # GENERAL_PUNCTUATION

        if self.select_ipa.get() > 0:
            character_list.extend(list(range(0x0250, 0x02AF + 1))) # IPA_EEXTENTIONS

        if self.select_symbols.get() > 0:
            character_list.extend(list(range(0x2190, 0x21FF + 1))) # ARROW_CHARS
            character_list.extend(list(range(0x2200, 0x22FF + 1))) # MATHEMATICAL_CHARS
            character_list.extend(list(range(0x2300, 0x23FF + 1))) # MISC_TECH_CHARS
            character_list.extend(list(range(0x2600, 0x26FF + 1))) # MISC_SYMBOLS
            character_list.extend(list(range(0x2700, 0x27BF + 1))) # DINGBATS

        if self.select_add_lang.get() > 0:
            character_list.extend(list(range(0x0370, 0x03FF + 1))) # GREEK_AND_COPTIC_CHARS
            character_list.extend(list(range(0x0400, 0x04FF + 1))) # CYRILLIC_CHARS
            character_list.extend(list(range(0x0500, 0x052F + 1))) # CYRILLIC_SUPPLEMENT_CHARS
            character_list.extend(list(range(0x0530, 0x058F + 1))) # ARMENIAN_CHARS
            character_list.extend(list(range(0x0590, 0x05FF + 1))) # HEBREW_CHARS
            character_list.extend(list(range(0x0600, 0x06FF + 1))) # ARABIC_CHARS
            character_list.extend(list(range(0x0700, 0x074F + 1))) # SYRIAC_CHARS
            character_list.extend(list(range(0x0750, 0x077F + 1))) # ARABIC_SUPPLEMENT_CHARS
            character_list.extend(list(range(0x4E00, 0x9FFF + 1))) # CJK_UNIFIED_IDEOGRAPHS_PART

        self.pb_progress['value'] = 0

        include_empty = False
        if self.include_empty_lbl.get() > 0:
            include_empty = True

        conv = Type2NC(output_folder=self.output_path, target_height=10, step_size=self.step_size, unicode_numbers=character_list, create_empty_labels=include_empty)
        self._log.debug("start processing %d font files", len(self.selected_font_files))
        
        if self.include_hershey.get() > 0:
            for hershey_font in HersheyFonts().default_font_names:
                conv.convert_hershey(hershey_font)
        
        for i, ff in enumerate(self.selected_font_files):
            if ff.is_file():
                if ff.suffix.lower() in ".jhf":
                    conv.convert_hershey(ff)
                else:
                    conv.convert_freetype(ff)
            self.pb_progress['value'] = (i + 1) * (100 / len(self.selected_font_files))
            self.pb_progress.update()

        if self.gen_demo_files.get() > 0:
            self._log.debug("generating demo files is enabled")
            conv.generate_demo_files(self.selected_font_files)

        tkmb.showinfo(parent=self._window_root, title=self.gt_("Finished"), message=self.gt_("Finished processing all font files"))

        self.lbl_font_filename["text"] = " "
        del self.selected_font_files[:]


if __name__ == "__main__":
    log_level_map = {'critical': logging.CRITICAL, 'error': logging.ERROR,
                     'warn': logging.WARNING, 'warning': logging.WARNING,
                     'info': logging.INFO, 'debug': logging.DEBUG}

    cmdl_parser = argparse.ArgumentParser(description="Create Klartext NC code from font files. If no options are given, start gui")
    cmdl_parser.add_argument("-i", "--input", metavar="font input file", nargs='+', type=pathlib.Path, help="path of one or more font files")
    cmdl_parser.add_argument("-o", "--output", metavar="output folder", type=pathlib.Path, help="path to the output folder where klartext files are generated")
    cmdl_parser.add_argument("-s", "--step_size", metavar="step size", type=float, default=0.05, required=False, help="step size for converting curves to line segmenst: between 0.001 (very fine) and 0.2 (very coarse)")
    cmdl_parser.add_argument("-d", "--create_demos", action="store_true", default=False, required=False, help="if set, demo output will use cycle 225 for definition of parameters")
    cmdl_parser.add_argument("-e", "--create_empty_label", action="store_true", default=False, required=False, help="if set, create label for each selected character, even if it is not defined in the font. Stops errors because of missing label definition")
    cmdl_parser.add_argument("-l", "--log", metavar="logging level", default="warning", help="set logging level to critical, error, warn/warning, info or debug. Default is info")
    cmdl_parser.add_argument("-m", "--message", metavar="message", default=None, type=str, help="Message to create as NCprogram")
    cmdl_parser.add_argument("-n", "--numeric",  action="store_true", default=False, required=False, help="Only create numeric numeric label calls for character selection. reduces available cahrset to ASCII. makes program compatible with older controls?")

    arguments = cmdl_parser.parse_args()

    selected_level = log_level_map.get(arguments.log.lower())

    if selected_level is None:
        raise Exception("the given log level {:s} can't be mapped to an existing log level. It must be one of critical, error, warn/warning, info or debug")
    logging.basicConfig(level=selected_level)
    logger = logging.getLogger('main')
    logger.info("startup")
    logger.setLevel(level=selected_level)

    if arguments.input is not None:
        if not arguments.output.is_dir():
            logger.error("The output path '%s' is not a folder", arguments.output)
            exit(-1)
        
        conv = Type2NC(output_folder=arguments.output, target_height=10,
                       step_size=arguments.step_size, create_empty_labels=arguments.create_empty_label,
                       only_numeric=arguments.numeric)

        for ff in arguments.input:
            if ff.is_file():
                if arguments.message is not None:
                    conv.convert_to_static(ff, arguments.message)
                else:
                    if ff.suffix.lower() in ".jhf":
                        conv.convert_hershey(ff)
                    else:
                        conv.convert_freetype(ff)
        
        if arguments.create_demos:
            conv.generate_demo_files(arguments.input)
    else:
        import tkinter.filedialog as tkfd
        import tkinter.simpledialog as tksd
        import tkinter.messagebox as tkmb
        import tkinter as tk
        import tkinter.ttk as ttk
        import tkinter.font as tkFont
        import gettext
        root = tk.Tk()
        app = Type2NC_UI(root)
        root.mainloop()

    logger.debug("finished")