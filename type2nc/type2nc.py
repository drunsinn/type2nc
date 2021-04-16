#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: drunsinn, TobFleischi, Klartext
'''

import datetime
import logging
import argparse
import pathlib
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
    def __init__(self, output_folder, target_height, step_size):
        self._log = logging.getLogger("Type2NC")
        self.__output_folder = output_folder.resolve(strict=True)
        self.__target_height = target_height
        self.__step_size = step_size
        self.__char_size = 64
        self._log.debug("using folder '%s', step size '%f'", self.__output_folder, self.__step_size)
    
    def convert(self, font_file):
        characters = string.ascii_letters + string.digits + string.punctuation

        self._log.debug("running for font file '%s'", font_file.resolve(strict=True))

        font_face = freetype.Face(str(font_file.resolve(strict=True)))
        self._log.debug("Font: %s, Style: %s, Format: %s", font_face.family_name.decode("utf-8"), font_face.style_name.decode("utf-8"), font_face.get_format().decode("utf-8"))
        font_face.set_char_size(height=self.__char_size)
        
        self._log.debug("Font BBox (min:max) X:(%d:%d) Y:(%d:%d)", font_face.bbox.xMax, font_face.bbox.xMin, font_face.bbox.yMax, font_face.bbox.yMin)
        scale_factor = self.__target_height / font_face.bbox.xMax
        self._log.debug("set scaling factor to %f", scale_factor)

        nc_file_name = font_file.name.replace(font_file.suffix, '.H')
        nc_file_name = nc_file_name.replace(' ', '_')
        nc_file_path = self.__output_folder.joinpath(nc_file_name)

        with open(nc_file_path, 'w') as ncfp:

            for char_str in list(characters):
                char_index = font_face.get_char_index(ord(char_str))
                if char_index > 0:
                    self._log.debug("character '%s' availible at index %d", char_str, char_index)

                    font_face.load_char(char_str)
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

class Type2NC_UI:
    def __init__(self, root):
        self._window_root = root
        root.title("type2nc")
        width=400
        height=210
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self._window_root.geometry(alignstr)
        self._window_root.resizable(width=False, height=False)

        ft = tkFont.Font(family='Times',size=12)

        self.btn_select_font=tk.Button(self._window_root)
        
        self.btn_select_font["font"] = ft
        self.btn_select_font["justify"] = "center"
        self.btn_select_font["text"] = "Select Font File"
        self.btn_select_font.place(x=20, y=20, width=160, height=30)
        self.btn_select_font["command"] = self.btn_select_font_command

        self.lbl_font_filename=tk.Label(self._window_root)
        self.lbl_font_filename["font"] = ft
        self.lbl_font_filename["justify"] = "center"
        self.lbl_font_filename["text"] = " "
        self.lbl_font_filename.place(x=200, y=20, width=180, height=30)

        self.btn_select_folder=tk.Button(self._window_root)
        self.btn_select_folder["font"] = ft
        self.btn_select_folder["justify"] = "center"
        self.btn_select_folder["text"] = "Select destination Folder"
        self.btn_select_folder.place(x=20, y=60, width=160, height=30)
        self.btn_select_folder["command"] = self.btn_select_folder_command

        self.lbl_output_path=tk.Label(self._window_root)
        self.lbl_output_path["font"] = ft
        self.lbl_output_path["justify"] = "center"
        self.lbl_output_path["text"] = " "
        self.lbl_output_path.place(x=200, y=60, width=180, height=30)

        self.btn_select_step=tk.Button(self._window_root)
        self.btn_select_step["font"] = ft
        self.btn_select_step["justify"] = "center"
        self.btn_select_step["text"] = "Select step size"
        self.btn_select_step.place(x=20, y=100, width=160, height=30)
        self.btn_select_step["command"] = self.btn_select_step_command

        self.lbl_step_size=tk.Label(self._window_root)
        self.lbl_step_size["font"] = ft
        self.lbl_step_size["justify"] = "center"
        self.lbl_step_size["text"] = " "
        self.lbl_step_size.place(x=200, y=100, width=180, height=30)
        
        self.btn_generate_nc=tk.Button(self._window_root)
        self.btn_generate_nc["font"] = ft
        self.btn_generate_nc["justify"] = "center"
        self.btn_generate_nc["text"] = "generate"
        self.btn_generate_nc.place(x=140, y=140, width=150, height=30)
        self.btn_generate_nc["command"] = self.btn_generate_nc_command

        self.pb_progress = ttk.Progressbar(self._window_root)
        self.pb_progress["orient"] = tk.HORIZONTAL
        self.pb_progress["length"] = 100
        self.pb_progress.place(x=115, y=170, width=200, height=30)
        self.pb_progress["mode"] = 'determinate'
        self.pb_progress['value'] = 0

        self.selected_font_files = list()
        self.output_path = None
        self.step_size = None


    def btn_select_font_command(self):
        file_types = [('Font', '*.ttf *.tte *.ttc *.otf *.dfont *.pfb')]
        font_file_list = tkfd.askopenfilename(parent=self._window_root, title="Select Font file", filetypes=file_types, multiple=1)
        for path in font_file_list:
            self.selected_font_files.append(pathlib.Path(path))

        if len(self.selected_font_files) == 1:
            self.lbl_font_filename["text"] = str(self.selected_font_files[0].name)
        else:
            self.lbl_font_filename["text"] = "%d files selected" % len(self.selected_font_files)

    def btn_select_folder_command(self):
        selected_folder = tkfd.askdirectory(parent=self._window_root, title="Select destination folder")
        self.output_path = pathlib.Path(selected_folder)

        if not self.output_path.is_dir():
            self.output_path = None
            self.lbl_output_path["text"] = "No folder selected"
        else:
            self.lbl_output_path["text"] = self.output_path.name

    def btn_select_step_command(self):
        selected_step = tksd.askfloat(parent=self._window_root, title="Step Size", prompt="Step Size between 0.001 (very fine) and 0.2 (very coarse) for converting Splines", initialvalue=0.05, minvalue=0.001, maxvalue=0.2)
        if selected_step is None:
            self.step_size = None
            self.lbl_step_size["text"] = "No step size selected"
        else:
            self.step_size = selected_step
            self.lbl_step_size["text"] = "%f" % self.step_size

    def btn_generate_nc_command(self):
        if len(self.selected_font_files) == 0:
            tkmb.showwarning(parent=self._window_root, title="Missing parameter", message="No font files selected")
            return
        if self.output_path is None:
            tkmb.showwarning(parent=self._window_root, title="Missing parameter", message="No output folder selected")
            return
        if self.step_size is None:
            tkmb.showwarning(parent=self._window_root, title="Missing parameter", message="No step size selected")
            return

        self.pb_progress['value'] = 0
        conv = Type2NC(output_folder=self.output_path, target_height=10, step_size=self.step_size)
        for i, ff in enumerate(self.selected_font_files):
            if ff.is_file():
                conv.convert(ff)
            self.pb_progress['value'] = (i + 1) * (100 / len(self.selected_font_files))

        tkmb.showwarning(parent=self._window_root, title="Finished", message="Finished processing all font files")

if __name__ == "__main__":
    logging.basicConfig(encoding='utf-8', level=logging.INFO)
    logger = logging.getLogger('main')
    logger.debug("startup")

    cmdl_parser = argparse.ArgumentParser(description="Create Klartext NC code from font files. If no options are given, start gui")
    cmdl_parser.add_argument("-i", "--input", metavar="font input file", nargs='+', type=pathlib.Path, help="path of one or more font files")
    cmdl_parser.add_argument("-o", "--output", metavar="output folder", type=pathlib.Path, help="path to the output folder where klartext files are generated")
    cmdl_parser.add_argument("-s", "--step_size", metavar="step size", type=float, default=0.05, required=False, help="step size for converting curves to line segmenst: between 0.001 (very fine) and 0.2 (very coarse)")

    arguments = cmdl_parser.parse_args()

    if arguments.input is not None:
        if not arguments.output.is_dir():
            logger.error("the output path '%s' is not a folder", arguments.output)
            
        conv = Type2NC(output_folder=arguments.output, target_height=10, step_size=arguments.step_size)
        for ff in arguments.input:
            if ff.is_file():
                
                conv.convert(ff)
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