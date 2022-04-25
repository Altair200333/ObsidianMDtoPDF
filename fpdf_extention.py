import numpy as np
from PIL import Image
import re
from css_parser import *
from fpdf import FPDF
from color_utils import *
from styles import *
import os.path

#http://www.fpdf.org/en/script/script74.php
class AlphaPDF (FPDF):
    def __init__ (self, orientation = 'P', unit = 'mm', format = 'A4'):
        self.__extgstates = []
        super().__init__ (orientation, unit, format)
        self.bm = 'Normal'
        self.alpha = 1
    # alpha: real value from 0 (transparent) to 1 (opaque)
    # bm:    blend mode, one of the following:
    #          Normal, Multiply, Screen, Overlay, Darken, Lighten, ColorDodge, ColorBurn,
    #          HardLight, SoftLight, Difference, Exclusion, Hue, Saturation, Color, Luminosity
    def set_alpha(self, alpha, bm='Normal'):
        # set alpha for stroking (CA) and non-stroking (ca) operations
        self.bm = bm
        self.alpha = alpha

        data = {'ca':alpha,'CA':alpha,'BM':'/' + bm, 'n' : 0}
        gs = self.add_ext_gstate(data)
        self.set_ext_gstate(gs + 1)

    def add_page(self, orientation=''):
        # do normal add page stuff
        super().add_page(orientation)
        self.set_alpha(self.alpha, self.bm)
        

    def add_ext_gstate(self, data):
        n = len(self.__extgstates)
        self.__extgstates.append(data)
        return n

    def _enddoc(self):
        if len(self.__extgstates) > 0 and self.pdf_version < '1.4':
            self.pdf_version ='1.4'
        super()._enddoc()

    def set_ext_gstate(self, gs):
        self._out('/GS%d gs' % (gs))

    def _putextgstates(self):
        i = 0
        while i < len(self.__extgstates):
            self._newobj()
            self._out('<</Type /ExtGState')
            self.__extgstates[i]["n"] = self.n
            parms = self.__extgstates[i]
            self._out('/ca %.3F' % (parms["ca"]))
            self._out('/CA %.3F' % (parms["CA"]))
            self._out('/BM ' + parms["BM"])
            self._out('>>')
            self._out('endobj')
            i += 1

    def _putresourcedict(self):
        super()._putresourcedict()
        self._out('/ExtGState <<')
        for index, eg in enumerate(self.__extgstates):
            self._out('/GS' + str(index + 1) + ' ' + str(eg["n"])  + ' 0 R')
        self._out('>>')

    def _putresources(self):
        self._putextgstates()
        super()._putresources()
        
class ColoredPDF (AlphaPDF):
    
    def __init__(self, orientation='P',unit='mm',format='A4'):
        super().__init__(orientation, unit, format)
        self.background_color = ""

    #hex color
    def set_background_color(self, color):
        if type(color) in (tuple, list, np.array) and (len(color) == 3 or len(color) == 4):
            color = rgb_to_hex(color)

        self.background_color = color
        
    def set_fill_color_str(self, fill_color):
        self.fill_color = fill_color
        self.color_flag=(self.fill_color!=self.text_color)
        if(self.page>0):
            self._out(self.fill_color)

    def add_page(self, orientation=''):
        # do normal add page stuff
        super().add_page(orientation)

        if self.background_color:
            # before pdf did it's content placement stuff insert background
            rgb = hex_to_rgba(self.background_color)

            last_alpha = self.alpha
            last_bm = self.bm
            last_fill = self.fill_color

            self.set_alpha(1)

            self.set_fill_color(rgb[0], rgb[1], rgb[2])
            self.rect(0,0, 210, 297, "F")

            self.set_alpha(last_alpha, last_bm)
            self.set_fill_color_str(last_fill)


class StyledPDF(ColoredPDF):
    def __init__(self, orientation='P',unit='mm',format='A4'):
        super().__init__(orientation, unit, format)

        self.set_doc_style(DocStyle())

        self.set_text_style(TextStyle())

    def set_doc_style(self, style: DocStyle):
        self.doc_style = style
        self.set_background_color(style.background_color)
        
    def set_text_style(self, style: TextStyle):
        self.text_style = style

        #self.set_font("Arial", '', size = style.font_size)

        font_name = "Arial"
        font_path = ""
        font_style = ""

        if style.bold:
            font_path = "arial_bold.ttf"
            font_style = "B"
        else:
            font_path = "arial.ttf"
            font_style = ""
        
        self.add_font(font_name, font_style, font_path, uni=True)
        self.set_font(font_name, font_style, style.font_size)

        self.set_text_color(style.font_color[0], style.font_color[1], style.font_color[2])

        if style.background_color is not None:
            self.set_fill_color(style.background_color[0], style.background_color[1], style.background_color[2])
        else:
            color = self.doc_style.background_color
            self.set_fill_color(color[0], color[1], color[2])

class PrintablePDF(StyledPDF):
    def __init__(self, orientation='P',unit='mm',format='A4'):
        self.text_buffer = ""
        self.cell_h = 10
        self.cell_w = 190

        self.pointer_x = 0
        self.pointer_y = 0
        
        super().__init__(orientation, unit, format)

    def bullet(self):
        self.cell(1, 7, '.', align =  'R')

    def _print_char(self, x):
        self.text_buffer += x

        if x == '\n':
            self.finish_print()

            self.pointer_x = self.l_margin
            self.pointer_y += self.cell_h
            self.set_xy(self.pointer_x, self.pointer_y)
    def print_char(self, x):
        if x == '\t':
            for i in range(4):
                self._print_char(' ')
        else:
            self._print_char(x)
            
    def finish_print(self):
        if not self.text_buffer:
            return
        
        ret = self.multi_cell(0, self.cell_h, self.text_buffer, split_only = True)
        
        fill = self.text_style.background_color is not None
        
        if len(ret) > 1:
            r = ret[0]
            self.cell(self.cell_w, self.cell_h, r, 0, 2, 'J', fill)

            self.set_x(self.l_margin)
            
            remaining_parts = ret[1:]
            text = " ".join(remaining_parts)
                
            ret = self.multi_cell(0, self.cell_h, text, split_only = True)                
        
        self.print_bloks(ret)
        

        self.text_buffer = ""
    
    def print_bloks(self, ret):
        fill = self.text_style.background_color is not None

        for r in ret:
            chars = self.get_string_width(r)# np.add.reduce([cw.get(c,0) for c in r])
            
            self.pointer_x = chars+ self.x# + self.l_margin 
            self.pointer_y = self.y

            self.cell(self.cell_w, self.cell_h, r, 0, 2, 'J', fill)

    def set_text_style(self, style: TextStyle):
        if self.text_buffer:
            self.finish_print()
            self.set_xy(self.pointer_x, self.pointer_y)
        
        super().set_text_style(style)