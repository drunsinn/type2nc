#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: drunsinn
'''

import os
import platform
import datetime
import string
import unicodedata
import tkinter as tk
import tkinter.filedialog, tkinter.simpledialog
import argparse
import numpy as np
from scipy.special import binom

if platform.system() == 'Windows' and os.path.isdir('./lib/'):
    os.environ["PATH"] += os.pathsep + './lib/'

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
    CJK_UNIFIED_IDEOGRAPHS_PART1 = list(range(0x4E00, 0x62FF + 1))
    CJK_UNIFIED_IDEOGRAPHS_PART2 = list(range(0x6300, 0x77FF + 1))
    CJK_UNIFIED_IDEOGRAPHS_PART3 = list(range(0x7800, 0x8CFF + 1))
    CJK_UNIFIED_IDEOGRAPHS_PART4 = list(range(0x8D00, 0x9FFF + 1))

    def __init__(self, bezier_step_size, char_list, output_folder, size_pt=50,
                 size_dpi=100, target_height=10):
        self.__bezier_step_size = bezier_step_size
        self.__char_list = char_list
        self.__output_folder = output_folder
        self.__charsize_pt = size_pt
        self.__charsize_dpi = size_dpi
        self.__chartarget_height = target_height
        self.__nc_file_list = list()

    def type2font(self, font_file_path):
        face = ft.Face(font_file_path)
        print("File: {0:s}, Font: {1:s}, Style: {2:s}, Number of characters:{3:d}".format(
              font_file_path,
              face.family_name.decode("utf-8"),
              face.style_name.decode("utf-8"),
              len(self.__char_list)))

        face.set_char_size(height=self.__charsize_pt * self.__charsize_dpi)

        char_lines = []
        char_data_collection = list()
        x_max = 0

        for char in self.__char_list:
            char_data = dict()
            char_data['plain'] = str(char)
            char_data['ord'] = ord(chr(char))
            char_data['paths'], char_data[
                'info'] = self.get_paths_of_char(face, char)
            char_data['text'] = self.get_label_name_from_char(char)
            char_data_collection.append(char_data)

            # find the highest charakter to calculate the scale factor
            if char_data['info']['x_max'] > x_max:
                x_max = char_data['info']['x_max']

        scale_factor = self.__chartarget_height / x_max

        for char_data in char_data_collection:
            try:
                plain_char_name = char_data['plain']
            except ValueError as e:
                plain_char_name = char_data['plain']
            if char_data['text'] is not None:
                char_lines.append('* -   {0:s}'.format(char_data['text']))
                char_lines.append('LBL "{0:s}"'.format(char_data['text']))
            else:
                char_lines.append('* -   Unicode Hex:0x{0:04x}: {1:s}'.format(
                        char_data['ord'], plain_char_name))
            char_lines.append('LBL "0x{0:04x}"'.format(char_data['ord']))

            for path in char_data['paths']:

                first_point = path[0]
                char_lines.append('L  X{0:+0.4f}  Y{1:+0.4f} FMAX'.format(
                    first_point[0] * scale_factor,
                    first_point[1] * scale_factor))
                char_lines.append('L  Z+QL15')

                for point in path[1:]:
                    char_lines.append('L  X{0:+0.4f}  Y{1:+0.4f}'.format(
                        point[0] * scale_factor, point[1] * scale_factor))

                if not (first_point[0] == point[0] and
                        first_point[1] == point[1]):
                    char_lines.append('L  X{0:+0.4f}  Y{1:+0.4f}'.format(
                        first_point[0] * scale_factor,
                        first_point[1] * scale_factor))

                char_lines.append('L  Z+Q1602')

            if char_data['text'] is not None:
                char_lines.append('LBL "{0:s}_X-Advance"'.format(
                    char_data['text']))
            char_lines.append('LBL "0x{0:04x}_X-Advance"'.format(
                char_data['ord']))

            char_lines.append('QL20 = {0:+f} ; X-Advance'.format(
                char_data['info']['x_advance'] * scale_factor))

            char_lines.append('LBL 0')
            char_lines.append(';')

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
        output_lines.append('; Number of Charakters: {0:d}'.format(
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
        print("Number of NC-Code lines: {0:d}, File size: {1:d} bytes".format(len(output_lines), file_size))
        return nc_file_name

    def get_point_on_bezier_curve(self, points, t):
        if t < 0.0 or t > 1.0:
            raise ValueError()
        n = len(points) - 1
        c_t_x = 0
        c_t_y = 0
        for i, point in enumerate(points):
            b_i_n = binom(n, i) * (t ** i) * np.power((1 - t), (n - i))
            c_t_x += b_i_n * point[0]
            c_t_y += b_i_n * point[1]
        return c_t_x, c_t_y

    def get_paths_of_char(self, fontFace, char):
        char_info = dict()
        fontFace.load_char(char)
        slot = fontFace.glyph
        outline = slot.outline
        paths = []

        if len(slot.outline.points) < 1:
            char_info['x_max'] = 0
            char_info['x_advance'] = slot.advance.x
            char_info['y_advance'] = slot.advance.y
        else:
            points = np.array(outline.points, dtype=[('x', float), ('y', float)])
            x, y = points['x'], points['y']
            start, end = 0, 0
            char_info['x_max'] = x.max()
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
                        for t in np.linspace(
                                0.0,
                                1.0,
                                1.0 / self.__bezier_step_size,
                                endpoint=True):
                            path_points.append(
                                self.get_point_on_bezier_curve(segment, t))

                paths.append(path_points)
                start = end + 1

        return paths, char_info

    def get_label_name_from_char(self, char):
        char = chr(char)
        if char in string.punctuation:
            if '!' in char:
                nameOfChar = 'exclamation_mark'
            elif '\'' in char:
                nameOfChar = 'apostrophe'
            elif '(' in char:
                nameOfChar = 'opening_parenthese'
            elif ')' in char:
                nameOfChar = 'closing_parenthese'
            elif '*' in char:
                nameOfChar = 'asterisk'
            elif '+' in char:
                nameOfChar = 'plus'
            elif '/' in char:
                nameOfChar = 'slash'
            elif ':' in char:
                nameOfChar = 'colon'
            elif ';' in char:
                nameOfChar = 'semicolon'
            elif '<' in char:
                nameOfChar = 'less_than'
            elif '=' in char:
                nameOfChar = 'equal'
            elif '>' in char:
                nameOfChar = 'greater_than'
            elif '?' in char:
                nameOfChar = 'question_mark'
            elif '@' in char:
                nameOfChar = 'at'
            elif '[' in char:
                nameOfChar = 'opening_square_brackets'
            elif '\\' in char:
                nameOfChar = 'backslash'
            elif ']' in char:
                nameOfChar = 'closing_square_brackets'
            elif '^' in char:
                nameOfChar = 'caret'
            elif '"' in char:
                nameOfChar = 'quotation_marks'
            elif '`' in char:
                nameOfChar = 'prime'
            elif '{' in char:
                nameOfChar = 'opening_braces'
            elif '|' in char:
                nameOfChar = 'pipe'
            elif '}' in char:
                nameOfChar = 'closing_braces'
            elif '~' in char:
                nameOfChar = 'tilde'
            else:
                nameOfChar = char
        elif char in string.ascii_letters + string.digits:
            nameOfChar = char
        elif 'ä' in char:
            nameOfChar = 'ae'
        elif 'ö' in char:
            nameOfChar = 'oe'
        elif 'ü' in char:
            nameOfChar = 'ue'
        elif 'Ä' in char:
            nameOfChar = 'AE'
        elif 'Ö' in char:
            nameOfChar = 'OE'
        elif 'Ü' in char:
            nameOfChar = 'UE'
        elif ' ' in char:
            nameOfChar = 'space'
        else:
            nameOfChar = None  # could not identify charakter
        return nameOfChar

    def generate_demo_file(self):
        output_file_path = os.path.join(self.__output_folder, "type2nc_demo.H")

        with open('demo_pgm_template.H', 'r') as templateFile:
            demo_file_content = templateFile.read()

        part_y_max = 10 + len(self.__nc_file_list) * 20 + 10
        current_y = 10

        filler = ""
        pgm_call_template = ';\nQ1603 = 10 ;Start X\nQ1604 = {0:d} ;Start Y\nQS1 = "{1:s}" || QS10\nCALL PGM {1:s}\n;'
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
        # type=argparse.FileType("r"),
        help="path and name of the font input file")
    parser.add_argument(
        "-o",
        "--out",
        metavar="output folder",
        # type=string,
        help="path and name of the font input file")
    parser.add_argument(
        "-s",
        "--step_size",
        metavar="step size",
        type=float,
        default=0.05,
        required=False,
        help="Step Size between 0.001 (very fine) and 0.2 (very coarse) for converting Splines")

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
    char_list += Type2NC.CJK_UNIFIED_IDEOGRAPHS_PART1
    char_list += Type2NC.CJK_UNIFIED_IDEOGRAPHS_PART2
    char_list += Type2NC.CJK_UNIFIED_IDEOGRAPHS_PART3
    char_list += Type2NC.CJK_UNIFIED_IDEOGRAPHS_PART4

    file_types = [('Font','*.ttf *.tte *.ttc *.otf *.dfont *.pfb')]

    if args.input is None:
        root = tk.Tk()
        root.overrideredirect(1)
        root.withdraw()

        font_file_list = tkinter.filedialog.askopenfilename(parent=root, title="Select Font file", filetypes=file_types,  multiple=1)
        if len(font_file_list) < 1:
            exit(-1)

        output_folder = tkinter.filedialog.askdirectory(parent=root, title="Select destination folder")
        if len(output_folder) < 1:
            exit(-2)

        step_size = tkinter.simpledialog.askfloat("Step Size",
                                            "Step Size between 0.001 (very fine) and 0.2 (very coarse) for converting Splines",
                                            initialvalue=0.05,
                                            minvalue=0.001,
                                            maxvalue=0.2)
        if step_size is None:
            exit(-3)

    else:
        font_file_list = args.input
        step_size = args.step_size
        output_folder = args.out

    font_converter = Type2NC(step_size, char_list, os.path.abspath(output_folder))

    for font_file in font_file_list:
        font_converter.type2font(os.path.abspath(font_file))

    font_converter.generate_demo_file()
