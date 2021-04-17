#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: drunsinn, TobFleischi, Klartext
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

class Point():
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
    
    def __str__(self):
        return "X:{:+0.4f} Y:{:+0.4f}".format(self.x, self.y)
    
    def scaled_str(self, scale_factor=1.0):
        return "X{:+0.4f} Y{:+0.4f}".format(self.x * scale_factor, self.y * scale_factor)

class Type2NC(object):
    BASIC_LATIN = (0x0020, 0x007E + 1)
    C1_CTRL_AND_LATIN1_SUPPLEMENT = (0x0080, 0x00FF + 1)
    IPA_EEXTENTIONS = (0x0250, 0x02AF + 1)
    GREEK_AND_COPTIC_CHARS = (0x0370, 0x03FF + 1)
    CYRILLIC_CHARS = (0x0400, 0x04FF + 1)
    CYRILLIC_SUPPLEMENT_CHARS = (0x0500, 0x052F + 1)
    ARMENIAN_CHARS = (0x0530, 0x058F + 1)
    HEBREW_CHARS = (0x0590, 0x05FF + 1)
    ARABIC_CHARS = (0x0600, 0x06FF + 1)
    SYRIAC_CHARS = (0x0700, 0x074F + 1)
    ARABIC_SUPPLEMENT_CHARS = (0x0750, 0x077F + 1)
    GENERAL_PUNCTUATION = (0x2000, 0x206F + 1)
    ARROW_CHARS = (0x2190, 0x21FF + 1)
    MATHEMATICAL_CHARS = (0x2200, 0x22FF + 1)
    MISC_TECH_CHARS = (0x2300, 0x23FF + 1)
    MISC_SYMBOLS = (0x2600, 0x26FF + 1)
    DINGBATS = (0x2700, 0x27BF + 1)
    CJK_UNIFIED_IDEOGRAPHS_PART = (0x4E00, 0x9FFF + 1)

    def __init__(self, output_folder, target_height, step_size):
        self._log = logging.getLogger("Type2NC")
        self.__output_folder = output_folder.resolve(strict=True)
        self.__target_height = target_height
        self.__step_size = step_size
        self.__char_size = 64
        self.__char_ranges = (self.BASIC_LATIN, self.C1_CTRL_AND_LATIN1_SUPPLEMENT, self.IPA_EEXTENTIONS, self.GREEK_AND_COPTIC_CHARS, self.CYRILLIC_CHARS,
                              self.CYRILLIC_SUPPLEMENT_CHARS, self.ARMENIAN_CHARS, self.HEBREW_CHARS, self.SYRIAC_CHARS, self.ARABIC_SUPPLEMENT_CHARS,
                              self.GENERAL_PUNCTUATION, self.GENERAL_PUNCTUATION, self.ARROW_CHARS, self.MATHEMATICAL_CHARS, self.MISC_TECH_CHARS, self.MISC_SYMBOLS,
                              self.DINGBATS, self.CJK_UNIFIED_IDEOGRAPHS_PART)
        self._log.debug("using folder '%s', step size '%f'", self.__output_folder, self.__step_size)
    
    def convert(self, font_file):
        characters = self._build_char_string(self.__char_ranges)

        self._log.debug("running for font file '%s' for %d characters", font_file.resolve(strict=True), len(characters))

        font_face = freetype.Face(str(font_file.resolve(strict=True)))
        self._log.info("Font: %s, Style: %s, Format: %s", font_face.family_name.decode("utf-8"), font_face.style_name.decode("utf-8"), font_face.get_format().decode("utf-8"))
        font_face.set_char_size(height=self.__char_size)
        
        self._log.info("Font BBox (min:max) X:(%d:%d) Y:(%d:%d)", font_face.bbox.xMax, font_face.bbox.xMin, font_face.bbox.yMax, font_face.bbox.yMin)
        scale_factor = self.__target_height / (abs(font_face.bbox.xMax) + abs(font_face.bbox.xMin))
        self._log.info("set scaling factor to %f", scale_factor)

        nc_file_name = font_file.name.replace(font_file.suffix, '.H')
        nc_file_name = nc_file_name.replace(' ', '_')
        nc_file_path = self.__output_folder.joinpath(nc_file_name)

        with open(nc_file_path, 'w') as ncfp:

            for char_str in list(characters):
                char_index = font_face.get_char_index(ord(char_str))
                if char_index > 0:
                    self._log.debug("character '%s' availible at index %d", char_str, char_index)

                    try:
                        font_face.load_char(char_str)
                    except freetype.ft_errors.FT_Exception as e:
                        self._log.error("character '%s' at index %d could not be loaded, skipp. Error: %s", char_str, char_index, e)
                        break

                    c_glyph_slot = font_face.glyph

                    contour_paths = list()

                    self._log.debug("character '%s' advance X:%d Y:%d", char_str, c_glyph_slot.advance.x, c_glyph_slot.advance.y)

                    if c_glyph_slot.outline.n_points > 0:
                        self._log.debug("character '%s' has %d points in %d contour(s) with %d tags", char_str, c_glyph_slot.outline.n_points, c_glyph_slot.outline.n_contours, len(c_glyph_slot.outline.tags))
                        
                        start, end = 0, 0

                        for i in range(0, c_glyph_slot.outline.n_contours):
                            path_points = list()
                            contour_segments = list()

                            end = c_glyph_slot.outline.contours[i] + 1
                            
                            # slice lists of points and tags according to length of contour
                            contour_tags = c_glyph_slot.outline.tags[start:end]
                            contour_points = c_glyph_slot.outline.points[start:end]

                            # add first point in list to segment to start things of
                            contour_segments.append([contour_points[0], ])

                            # split the list of all the points in separate segments
                            # with the right amount for each contour type
                            for j in range(0, len(contour_points)):
                                # skip first point as it is already in the list
                                contour_segments[-1].append(contour_points[j])
                                if contour_tags[j] & (1 << 0) and j < (len(contour_points) - 1):
                                    contour_segments.append([contour_points[j], ])

                            # finaly, check each segment for the number of points it contains.
                            # if only two the segmet is a line so we can just add the end point to our list
                            # if there are more than two points in the segment we have to step along the bezier curve
                            for segment in contour_segments:
                                if len(segment) == 2:  # line segment, add endpoint to list
                                    path_points.append(Point(x=segment[0][0], y=segment[0][1]))
                                else:  # bezier curve, split into segments an add them to list
                                    num_points = int(1.0 / self.__step_size)
                                    for t in np.linspace(0.0, 1.0, num_points, endpoint=True):
                                        path_points.append(self._point_on_curve(segment, t))

                            start = end
                            
                            path_points.append(Point(x=contour_segments[0][0][0], y=contour_segments[0][0][1])) # close path by addind the first point a second time
                            
                            contour_paths.append(path_points)
                            self._log.debug("created %d points for character contour %d",  len(path_points), i)

                        self._log.debug("created %d paths for character", len(contour_paths))

                    else:
                        self._log.debug("character '%s' is empty, skipping", char_str)

                    ncfp.write("BEGIN PGM {0:s} MM\n".format(font_file.name.replace(font_file.suffix, '').upper()))
                    
                    ncfp.write(";\n; Font PGM generated by type2nc\n")
                    ncfp.write("; {0:s} - {1:s}\n".format(font_face.family_name.decode("utf-8"), font_face.style_name.decode("utf-8")))
                    ncfp.write("; Generated: {:%Y-%m-%d %H:%M:%S}\n".format(datetime.datetime.today()))
                    ncfp.write("; Number of characters: {0:d}\n;\n".format(len(characters)))

                    with open(pathlib.Path.cwd().joinpath("templates", "pgm_head_template.H")) as template_file:
                        ncfp.writelines(template_file)

                    ncfp.writelines(self._creat_font_label(char_str, contour_paths, c_glyph_slot.advance.x, scale_factor))

                    with open(pathlib.Path.cwd().joinpath("templates", "pgm_foot_template.H")) as template_file:
                        ncfp.writelines(template_file)

                    ncfp.write("END PGM {0:s} MM".format(font_file.name.replace(font_file.suffix, '').upper()))

                else:
                    self._log.debug("character '%s' was selected but is not availible, skipping", char_str)
        self._log.info("finished writing %s", nc_file_name)

    def _build_char_string(self, range_list):
        characters = ""
        for char_range in range_list:
            for i in range(char_range[0], char_range[1]):
                characters += chr(i)

        return characters

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
        self._log.debug("created lable for char %s", char_str)
        char_lines = list()
        label_name = self._translate_lable_name(char_str)
        self._log.debug("writing label for character '%s': %d %s", char_str, ord(char_str), label_name)

        char_lines.append("* -   {0:s}\n".format(char_str))
        if label_name is not None:
            char_lines.append("LBL \"{0:s}\"\n".format(label_name))
            char_lines.append("* -   Unicode Hex:0x{0:04x} : {1:s}\n".format(ord(char_str), label_name))
        else:
            char_lines.append("* -   Unicode Hex:0x{0:04x}\n".format(ord(char_str)))
        char_lines.append("LBL \"0x{0:04x}\"\n".format(ord(char_str)))
        
        for path in contour_paths:
            char_lines.append("L {0:s} FMAX\n".format(path[0].scaled_str()))
            char_lines.append("L Z+QL15 F+Q206\n")
            for point in path[1:]:
                char_lines.append("L {0:s} F+Q207\n".format(point.scaled_str()))
            #if not (path[0] == point and path[0][1] == point[1]):
            #    char_lines.append("L  X{0:+0.4f}  Y{1:+0.4f} F+Q207".format(path[0][0] * scale_factor, path[0][1] * scale_factor))
            char_lines.append("L Z+Q204 F AUTO\n")

        if label_name is not None: char_lines.append("LBL \"{0:s}_X-Advance\"\n".format(label_name))
        char_lines.append("LBL \"0x{0:04x}_X-Advance\"\n".format(ord(char_str)))
        char_lines.append("QL20 = {0:+f} ; X-Advance\n".format(x_advance))
        char_lines.append("LBL 0\n;\n")
        return char_lines

    def _translate_lable_name(self, char_str):
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
    
class Type2NC_UI:
    def __init__(self, root):
        self._log = logging.getLogger("Type2NCUI")
        self._log.debug("start building tk ui")
        self._window_root = root
        root.title("type2nc")
        width=400
        height=250
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self._window_root.geometry(alignstr)
        self._window_root.resizable(width=False, height=False)

        ft = tkFont.Font(family='Times',size=12)

        current_y = 20
        delta_y = 40
        component_height = 30

        self.btn_select_font = tk.Button(self._window_root)
        self.btn_select_font["font"] = ft
        self.btn_select_font["justify"] = "center"
        self.btn_select_font["text"] = "Select Font File"
        self.btn_select_font.place(x=20, y=current_y, width=160, height=component_height)
        self.btn_select_font["command"] = self.btn_select_font_command

        self.lbl_font_filename = tk.Label(self._window_root)
        self.lbl_font_filename["font"] = ft
        self.lbl_font_filename["justify"] = "center"
        self.lbl_font_filename["text"] = " "
        self.lbl_font_filename.place(x=200, y=current_y, width=180, height=component_height)
        current_y += delta_y

        self.btn_select_folder = tk.Button(self._window_root)
        self.btn_select_folder["font"] = ft
        self.btn_select_folder["justify"] = "center"
        self.btn_select_folder["text"] = "Select destination Folder"
        self.btn_select_folder.place(x=20, y=current_y, width=160, height=component_height)
        self.btn_select_folder["command"] = self.btn_select_folder_command

        self.lbl_output_path = tk.Label(self._window_root)
        self.lbl_output_path["font"] = ft
        self.lbl_output_path["justify"] = "center"
        self.lbl_output_path["text"] = " "
        self.lbl_output_path.place(x=200, y=current_y, width=180, height=component_height)
        current_y += delta_y

        self.btn_select_step = tk.Button(self._window_root)
        self.btn_select_step["font"] = ft
        self.btn_select_step["justify"] = "center"
        self.btn_select_step["text"] = "Select step size"
        self.btn_select_step.place(x=20, y=current_y, width=160, height=component_height)
        self.btn_select_step["command"] = self.btn_select_step_command

        self.lbl_step_size = tk.Label(self._window_root)
        self.lbl_step_size["font"] = ft
        self.lbl_step_size["justify"] = "center"
        self.lbl_step_size["text"] = " "
        self.lbl_step_size.place(x=200, y=current_y, width=180, height=component_height)
        current_y += delta_y

        self.gen_demo_files = tk.IntVar()
        self.chk_generate_demos = tk.Checkbutton(self._window_root)
        self.chk_generate_demos["font"] = ft
        self.chk_generate_demos["justify"] = "left"
        self.chk_generate_demos["text"] = "Create demo files"
        self.chk_generate_demos.place(x=20, y=current_y, width=150, height=component_height)
        self.chk_generate_demos["onvalue"] = 1
        self.chk_generate_demos["offvalue"] = 0
        self.chk_generate_demos.select()
        self.chk_generate_demos["variable"] = self.gen_demo_files
        current_y += delta_y

        self.btn_generate_nc = tk.Button(self._window_root)
        self.btn_generate_nc["font"] = ft
        self.btn_generate_nc["justify"] = "center"
        self.btn_generate_nc["text"] = "generate"
        self.btn_generate_nc.place(x=140, y=current_y, width=150, height=component_height)
        self.btn_generate_nc["command"] = self.btn_generate_nc_command
        current_y += delta_y

        self.pb_progress = ttk.Progressbar(self._window_root)
        self.pb_progress["orient"] = tk.HORIZONTAL
        self.pb_progress["length"] = 100
        self.pb_progress.place(x=115, y=current_y, width=200, height=component_height)
        self.pb_progress["mode"] = 'determinate'
        self.pb_progress['value'] = 0
        current_y += delta_y

        self._log.debug("ui ready")

        self.selected_font_files = list()
        self.output_path = None
        self.step_size = None

    def btn_select_font_command(self):
        self._log.debug("select font button pressed")
        file_types = [('Font', '*.ttf *.tte *.ttc *.otf *.dfont *.pfb')]
        font_file_list = tkfd.askopenfilename(parent=self._window_root, title="Select Font file", filetypes=file_types, multiple=1)
        for path in font_file_list:
            self.selected_font_files.append(pathlib.Path(path))

        if len(self.selected_font_files) == 1:
            self.lbl_font_filename["text"] = str(self.selected_font_files[0].name)
            self._log.debug("No font file selected")
        else:
            self.lbl_font_filename["text"] = "%d files selected" % len(self.selected_font_files)
            self._log.debug("Add %d fonts to list: %s", len(font_file_list), font_file_list)

    def btn_select_folder_command(self):
        self._log.debug("select output folder button pressed")
        selected_folder = tkfd.askdirectory(parent=self._window_root, title="Select destination folder")
        self.output_path = pathlib.Path(selected_folder)

        if not self.output_path.is_dir():
            self.output_path = None
            self.lbl_output_path["text"] = "No folder selected"
            self._log.debug("No folder selected")
        else:
            self.lbl_output_path["text"] = self.output_path.name
            self._log.debug("Output folder set to %s", self.output_path)

    def btn_select_step_command(self):
        self._log.debug("select step size button pressed")
        selected_step = tksd.askfloat(parent=self._window_root, title="Step Size", prompt="Step Size between 0.001 (very fine) and 0.2 (very coarse) for converting Splines", initialvalue=0.05, minvalue=0.001, maxvalue=0.2)
        if selected_step is None:
            self.step_size = None
            self.lbl_step_size["text"] = "No step size selected"
            self._log.debug("No step size selected")
        else:
            self.step_size = selected_step
            self.lbl_step_size["text"] = "%f" % self.step_size
            self._log.debug("step size set to %f", self.step_size)

    def btn_generate_nc_command(self):
        self._log.debug("generate nc files button pressed")
        if len(self.selected_font_files) == 0:
            tkmb.showwarning(parent=self._window_root, title="Missing parameter", message="No font files selected")
            self._log.debug("list of selected font files is empty!")
            return
        if self.output_path is None:
            tkmb.showwarning(parent=self._window_root, title="Missing parameter", message="No output folder selected")
            self._log.debug("no output path selected!")
            return
        if self.step_size is None:
            tkmb.showwarning(parent=self._window_root, title="Missing parameter", message="No step size selected")
            self._log.debug("no step size selected selected!")
            return

        self.pb_progress['value'] = 0
        conv = Type2NC(output_folder=self.output_path, target_height=10, step_size=self.step_size)
        self._log.debug("start processing %d font files", len(self.selected_font_files))
        for i, ff in enumerate(self.selected_font_files):
            if ff.is_file():
                conv.convert(ff)
            self.pb_progress['value'] = (i + 1) * (100 / len(self.selected_font_files))

        if self.gen_demo_files.get() > 0:
            self._log.debug("generating demo files is enabled")
            conv.generate_demo_files(self.selected_font_files)

        tkmb.showwarning(parent=self._window_root, title="Finished", message="Finished processing all font files")

        self.lbl_font_filename["text"] = " "
        del self.selected_font_files[:]

if __name__ == "__main__":
    logging.basicConfig(encoding='utf-8', level=logging.INFO)
    logger = logging.getLogger('main')
    logger.debug("startup")

    cmdl_parser = argparse.ArgumentParser(description="Create Klartext NC code from font files. If no options are given, start gui")
    cmdl_parser.add_argument("-i", "--input", metavar="font input file", nargs='+', type=pathlib.Path, help="path of one or more font files")
    cmdl_parser.add_argument("-o", "--output", metavar="output folder", type=pathlib.Path, help="path to the output folder where klartext files are generated")
    cmdl_parser.add_argument("-s", "--step_size", metavar="step size", type=float, default=0.05, required=False, help="step size for converting curves to line segmenst: between 0.001 (very fine) and 0.2 (very coarse)")
    cmdl_parser.add_argument("-d", "--create_demos", action='store_true', default=False, required=False, help="if set, demo output will use cycle 225 for definition of parameters")
    arguments = cmdl_parser.parse_args()

    if arguments.input is not None:
        if not arguments.output.is_dir():
            logger.error("the output path '%s' is not a folder", arguments.output)
            
        conv = Type2NC(output_folder=arguments.output, target_height=10, step_size=arguments.step_size)
        for ff in arguments.input:
            if ff.is_file():
                
                conv.convert(ff)
        
        if arguments.create_demos:
            conv.generate_demo_files(arguments.input)
    else:
        import tkinter.filedialog as tkfd
        import tkinter.simpledialog as tksd
        import tkinter.messagebox as tkmb
        import tkinter as tk
        import tkinter.ttk as ttk
        import tkinter.font as tkFont
        root = tk.Tk()
        app = Type2NC_UI(root)
        root.mainloop()

    logger.debug("finished")