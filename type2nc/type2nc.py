#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: drunsinn, TobFleischi, Klartext
'''

import os
import platform
import datetime
import string
import tkinter as tk
import tkinter.filedialog as tkfd
import tkinter.simpledialog as tksd
import tkinter.messagebox as tkmb
import argparse
import numpy as np
from scipy.special import binom
import freetype as ft


class Type2NC(object):
    BASIC_LATIN = list(range(0x0020, 0x007E + 1))
    C1_CTRL_AND_LATIN1_SUPPLEMENT = list(range(0x0080, 0x00FF + 1))
    IPA_EEXTENTIONS = list(range(0x0250, 0x02AF + 1))
    GREEK_AND_COPTIC_CHARS = list(range(0x0370, 0x03FF + 1))
    CYRILLIC_CHARS = list(range(0x0400, 0x04FF + 1))
    CYRILLIC_SUPPLEMENT_CHARS = list(range(0x0500, 0x052F + 1))
    ARMENIAN_CHARS = list(range(0x0530, 0x058F + 1))
    HEBREW_CHARS = list(range(0x0590, 0x05FF + 1))
    ARABIC_CHARS = list(range(0x0600, 0x06FF + 1))
    SYRIAC_CHARS = list(range(0x0700, 0x074F + 1))
    ARABIC_SUPPLEMENT_CHARS = list(range(0x0750, 0x077F + 1))
    GENERAL_PUNCTUATION = list(range(0x2000, 0x206F + 1))
    ARROW_CHARS = list(range(0x2190, 0x21FF + 1))
    MATHEMATICAL_CHARS = list(range(0x2200, 0x22FF + 1))
    MISC_TECH_CHARS = list(range(0x2300, 0x23FF + 1))
    MISC_SYMBOLS = list(range(0x2600, 0x26FF + 1))
    DINGBATS = list(range(0x2700, 0x27BF + 1))
    CJK_UNIFIED_IDEOGRAPHS_PART = list(range(0x4E00, 0x9FFF + 1))

    MODE_ALL = 1
    MODE_REDUCE = 2
    MODE_REMOVE = 3

    def __init__(self, bezier_step_size, char_list, output_folder, size_pt=50,
                 size_dpi=100, target_height=10, output_mode=MODE_ALL):
        self.__bezier_step_size = bezier_step_size
        self.__char_list = char_list
        self.__output_folder = output_folder
        self.__char_size_pt = size_pt
        self.__char_size_dpi = size_dpi
        self.__char_target_height = target_height
        self.__output_mode = output_mode
        self.__nc_file_list = list()

    def type2font(self, font_file_path):
        face = ft.Face(font_file_path)
        print("File: {0:s}".format(font_file_path))
        print("Font: {0:s}, Style: {1:s}".format(
            face.family_name.decode("utf-8"),
            face.style_name.decode("utf-8")))

        face.set_char_size(height=self.__char_size_pt * self.__char_size_dpi)

        char_lines = []
        char_data_collection = list()
        empty_char_list = list()
        x_max = 0

        for char in self.__char_list:
            if face.get_char_index(char) == 0 and char != u"\u0020" and self.__output_mode is not Type2NC.MODE_ALL:
                empty_char_list.append(char)
            else:
                char_data = dict()
                char_data['plain'] = str(char)
                char_data['ord'] = ord(chr(char))
                char_data['paths'], char_data[
                    'info'] = self._get_paths_of_char(face, char)
                char_data['text'] = self._get_char_name(char)
                char_data_collection.append(char_data)
                # find the highest character to calculate the scale factor
                if char_data['info']['x_max'] > x_max:
                    x_max = char_data['info']['x_max']
        scale_factor = self.__char_target_height / x_max

        for char_data in char_data_collection:
            char_lines.extend(self._create_char_label(char_data, scale_factor))

        if self.__output_mode is Type2NC.MODE_REDUCE:
            char_lines.extend(self._create_empty_label(empty_char_list,
                                                       scale_factor,
                                                       face))

        nc_file_name = os.path.basename(font_file_path).split('.')[0] + '.H'
        nc_file_name = nc_file_name.replace(' ', '_')
        self.__nc_file_list.append(nc_file_name)
        output_file_path = os.path.join(self.__output_folder, nc_file_name)

        output_lines = []
        output_lines.append('BEGIN PGM {0:s} MM'.format(nc_file_name.upper()))
        output_lines.append(';')
        output_lines.append('; Font PGM generated by type2nc')
        output_lines.append('; {0:s} - {1:s}'.format(
            face.family_name.decode("utf-8"),
            face.style_name.decode("utf-8")))
        output_lines.append('; Generated: {:%Y-%m-%d %H:%M:%S}'.format(
                         datetime.datetime.today()))
        output_lines.append('; Number of characters: {0:d}'.format(
                         len(self.__char_list)))
        output_lines.append(';')

        with open('pgm_head_template.H', 'r') as templateFile:
            for line in templateFile:
                output_lines.append(line.rstrip('\n').rstrip('\r'))

        output_lines.append(';')

        output_lines.extend(char_lines)

        with open('pgm_foot_template.H', 'r') as templateFile:
            for line in templateFile:
                output_lines.append(line.rstrip('\n').rstrip('\r'))

        output_lines.append('END PGM {0:s} MM'.format(nc_file_name.upper()))

        output_fp = open(output_file_path, 'w')
        for i, line in enumerate(output_lines):
            output_fp.write('{0:d} {1:s}\n'.format(i, line))
        output_fp.close()

        file_size = os.path.getsize(output_file_path)
        if self.__output_mode is Type2NC.MODE_REDUCE or self.__output_mode is Type2NC.MODE_REMOVE:
            print("{0:d} of {1:d} selected characters were found empty".format(
                len(empty_char_list),
                len(self.__char_list)))
        else:
            print("{0:d} characters were selected".format(
                len(self.__char_list)))
        print("lines: {0:d}, file size: {1:d} bytes".format(len(output_lines),
                                                            file_size))

    def _create_empty_label(self, empty_chars, scale_factor, font_face):
        lable_lines = list()
        for char in empty_chars:
            lable_lines.append('LBL "0x{0:04x}"'.format(ord(chr(char))))

        self._get_paths_of_char(font_face, empty_chars[1])

        path, info = self._get_paths_of_char(font_face, empty_chars[1])

        lable_lines.extend(self._generate_path_lines(path,
                                                     scale_factor))
        lable_lines.append('QL20 = {0:+f} ; X-Advance'.format(
                           info['x_advance'] * scale_factor))
        lable_lines.append('LBL 0')
        return lable_lines

    def _create_char_label(self, char_data, scale_factor):
        """Generate klartext code for character

        Keyword arguments:
        char_data -- information on the character
        scale_factor -- factor for scaling the x and y values
        """
        char_lines = list()
        # plain_char_name = char_data['plain']
        if char_data['text'] is not None:
            char_lines.append('* -   {0:s}'.format(char_data['text']))
            char_lines.append('LBL "{0:s}"'.format(char_data['text']))
        char_lines.append('* -   Unicode Hex:0x{0:04x} : {1:s}'.format(
            char_data['ord'], char_data['plain']))
        char_lines.append('LBL "0x{0:04x}"'.format(char_data['ord']))

        char_lines.extend(self._generate_path_lines(char_data['paths'],
                                                    scale_factor))

        if char_data['text'] is not None:
            char_lines.append('LBL "{0:s}_X-Advance"'.format(char_data['text']))
        char_lines.append('LBL "0x{0:04x}_X-Advance"'.format(char_data['ord']))
        char_lines.append('QL20 = {0:+f} ; X-Advance'.format(
            char_data['info']['x_advance'] * scale_factor))
        char_lines.append('LBL 0')
        char_lines.append(';')
        return char_lines

    def _generate_path_lines(self, path_data, scale_factor):
        path_lines = list()
        for path in path_data:
            path_lines.append('L  X{0:+0.4f}  Y{1:+0.4f} FMAX'.format(
                path[0][0] * scale_factor,
                path[0][1] * scale_factor))
            path_lines.append('L  Z+QL15 F+Q206')
            for point in path[1:]:
                path_lines.append('L  X{0:+0.4f}  Y{1:+0.4f} F+Q207'.format(
                    point[0] * scale_factor, point[1] * scale_factor))
            if not (path[0][0] == point[0] and
                    path[0][1] == point[1]):
                path_lines.append('L  X{0:+0.4f}  Y{1:+0.4f} F+Q207'.format(
                    path[0][0] * scale_factor,
                    path[0][1] * scale_factor))
            path_lines.append('L  Z+Q204 F AUTO')

        return path_lines

    def _point_on_curve(self, point_list, distance_factor):
        """Get x and y coordinate for point along a bezier curve relative to
        the lenght of the curve.

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
            b_i_n = binom(n, i) * (distance_factor ** i) *\
                    np.power((1 - distance_factor), (n - i))
            c_t_x += b_i_n * point[0]
            c_t_y += b_i_n * point[1]
        return c_t_x, c_t_y

    def _get_paths_of_char(self, font_face, char):
        """Get list of x and y coordinates the outline of a character. Also
        returns information about the charkter.

        Keyword arguments:
        font_face -- freetype font face from the selected font file
        char -- character which should be converted
        """
        char_info = dict()
        font_face.load_char(char)
        slot = font_face.glyph
        outline = slot.outline
        paths = []

        if len(slot.outline.points) < 1:
            char_info['x_max'] = 0
            # char_info['x_min'] = 0
            char_info['x_advance'] = slot.advance.x
            char_info['y_advance'] = slot.advance.y
        else:
            points = np.array(outline.points,
                              dtype=[('x', float), ('y', float)])
            x = points['x']
            start, end = 0, 0
            char_info['x_max'] = x.max()
            # char_info['x_min'] = x.min()
            char_info['x_advance'] = slot.advance.x
            char_info['y_advance'] = slot.advance.y

            # iterate over each contour
            for i in range(len(outline.contours)):
                end = outline.contours[i]  # upper end of contour points
                points = outline.points[start:end + 1]  # contour points

                points.append(points[0])

                # list of contour types
                tags = outline.tags[start:end + 1]
                tags.append(tags[0])

                segments = [[points[0], ], ]

                path_points = []
                path_points.append(points[0])

                # split the list of all the points in seperate parts
                # with the right amount for each contour type
                for j in range(1, len(points)):
                    # skipp first point as it is already in the list
                    segments[-1].append(points[j])
                    if tags[j] & (1 << 0) and j < (len(points) - 1):
                        segments.append([points[j], ])

                for segment in segments:
                    if len(segment) == 2:  # straight segment
                        path_points.append(segment[-1])
                    else:
                        num_points = int(1.0 / self.__bezier_step_size)
                        for t in np.linspace(
                                0.0,
                                1.0,
                                num_points,
                                endpoint=True):
                            path_points.append(
                                self._point_on_curve(segment, t))

                paths.append(path_points)
                start = end + 1

        return paths, char_info

    def _get_char_name(self, char):
        """Get name of character for label call.

        Keyword arguments:
        char -- character
        """
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

        char = chr(char)

        if char in label_map.keys():
            label_name = label_map[char]
        elif char in string.ascii_letters + string.digits + string.punctuation:
            label_name = char
        else:
            label_name = None  # could not identify character
        return label_name

    def generate_demo_file(self, use_cycle_def=False):
        output_file_path = os.path.join(self.__output_folder, "type2nc_demo.H")

        if use_cycle_def:
            demo_template = 'demo_pgm_template_cycle.H'
        else: 
            demo_template = 'demo_pgm_template_conventional.H'

        with open(demo_template, 'r') as templateFile:
            demo_file_content = templateFile.read()

        part_y_max = 10 + len(self.__nc_file_list) * 20 + 10
        current_y = 10

        filler = ""
        pgm_call_template = 'L X+5 Y+5 Z+100 R0 FMAX\n'
        pgm_call_template += 'CALL PGM {1:s}\n;'
        for file_path in self.__nc_file_list:
            filler += pgm_call_template.format(current_y, file_path)
            current_y += 20

        output_fp = open(output_file_path, 'w')
        output_fp.write(demo_file_content.format(part_y_max, filler))
        output_fp.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create Klartext NC code from font files")
    parser.add_argument(
        "-i",
        "--input",
        metavar="font input file",
        nargs='+',
        help="path of one or more font files")
    parser.add_argument(
        "-o",
        "--out",
        metavar="output folder",
        required=False,
        help="path to the output folder. If not set, use current directory.")
    parser.add_argument(
        "-s",
        "--step_size",
        metavar="step size",
        type=float,
        default=0.05,
        required=False,
        help="step size: between 0.001 (very fine) and 0.2 (very coarse)")
    parser.add_argument(
        "-r",
        "--remove_empty",
        action='store_true',
        default=False,
        help="if set, output wont contain lables for empty chars. overrides -c")
    parser.add_argument(
        "-c",
        "--reduce_empty",
        action='store_true',
        default=False,
        help="if set, output will contain labels for empty characters but no actual data")
    parser.add_argument(
        "-z",
        "--use_cycle_def",
        action='store_true',
        default=False,
        help="if set, demo output will use cycle 225 for definiton of parametes")

    args = parser.parse_args()

    char_list = list()
    char_list = Type2NC.BASIC_LATIN
    char_list += Type2NC.C1_CTRL_AND_LATIN1_SUPPLEMENT
    char_list += Type2NC.IPA_EEXTENTIONS
    char_list += Type2NC.GREEK_AND_COPTIC_CHARS
    char_list += Type2NC.CYRILLIC_CHARS
    char_list += Type2NC.CYRILLIC_SUPPLEMENT_CHARS
    char_list += Type2NC.ARMENIAN_CHARS
    char_list += Type2NC.HEBREW_CHARS
    char_list += Type2NC.ARABIC_CHARS
    char_list += Type2NC.SYRIAC_CHARS
    char_list += Type2NC.ARABIC_SUPPLEMENT_CHARS
    char_list += Type2NC.GENERAL_PUNCTUATION
    char_list += Type2NC.ARROW_CHARS
    char_list += Type2NC.MATHEMATICAL_CHARS
    char_list += Type2NC.MISC_TECH_CHARS
    char_list += Type2NC.MISC_SYMBOLS
    char_list += Type2NC.DINGBATS
    char_list += Type2NC.CJK_UNIFIED_IDEOGRAPHS_PART

    file_types = [('Font', '*.ttf *.tte *.ttc *.otf *.dfont *.pfb')]

    if args.input is None:
        root = tk.Tk()
        root.overrideredirect(1)
        root.withdraw()

        font_file_list = tkfd.askopenfilename(parent=root,
                                              title="Select Font file",
                                              filetypes=file_types,
                                              multiple=1)
        if len(font_file_list) < 1:
            exit(-1)

        output_folder = tkfd.askdirectory(parent=root,
                                          title="Select destination folder")
        if len(output_folder) < 1:
            exit(-2)

        remove_empty = tkmb.askyesno("Remove empty", "Remove empty characters from output?")

        if not remove_empty:
            reduce_empty = tkmb.askyesno("Reduce empty", "Reduce filesize by reducing empty characters?")

        step_size = tksd.askfloat("Step Size",
                                  "Step Size between 0.001 (very fine) and 0.2 (very coarse) for converting Splines",
                                  initialvalue=0.05,
                                  minvalue=0.001,
                                  maxvalue=0.2)
        if step_size is None:
            exit(-3)

    else:
        font_file_list = args.input
        step_size = args.step_size
        if args.out is None:
            output_folder = os.getcwd()
        else:
            output_folder = args.out
        remove_empty = args.remove_empty
        reduce_empty = args.reduce_empty

    if remove_empty:
        mode_select = Type2NC.MODE_REMOVE
    elif reduce_empty:
        mode_select = Type2NC.MODE_REDUCE
    else:
        mode_select = Type2NC.MODE_ALL

    font_converter = Type2NC(bezier_step_size=step_size,
                             char_list=char_list,
                             output_folder=os.path.abspath(output_folder),
                             output_mode=mode_select)

    for font_file in font_file_list:
        font_converter.type2font(os.path.abspath(font_file))

    font_converter.generate_demo_file(args.use_cycle_def)
