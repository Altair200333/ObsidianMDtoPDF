from math import fabs
from src.css.color_utils import *

def try_convert_color(color):
    if type(color) is str:
        color = hex_to_rgba(color)
    return color
    
class TextStyle:
    def __init__(self, font_size = 16, font_color = [5, 5, 5], background_color = None, bold = False):
        self.font_size = font_size
        
        self.font_color = try_convert_color(font_color)
        self.background_color = try_convert_color(background_color) 
        self.bold = bold

    def set_font_color(self, color):
        self.font_color = try_convert_color(color)

    def set_background_color(self, color):
        self.background_color = try_convert_color(color)


class DocStyle:
    def __init__(self, background_color = [220, 220, 220]):
        self.background_color = try_convert_color(background_color)

    def set_background_color(self, color):
        self.background_color = try_convert_color(color)


class StylePool:
    def __init__(self):
        self.doc_style = DocStyle()

        self.style_normal = TextStyle(14, "#000066")
        self.style_normal2 = TextStyle(14, "#ff5050")

        self.style_h1 = TextStyle(28, "#ff33cc", bold=True)
        self.style_h2 = TextStyle(26, "#33cccc", bold=True)
        self.style_h3 = TextStyle(24, "#cc6600", bold=True)
        self.style_h4 = TextStyle(22, "#0000ff", bold=True)
        self.style_h5 = TextStyle(20, "#660066", bold=True)
        self.style_h5 = TextStyle(18, "#ff33cc", bold=True)
        self.style_h6 = TextStyle(16, "#000066", bold=True)

        self.style_mark = TextStyle(16, "#000099", "cc6699")
        self.style_code = TextStyle(16, "#000099", "000066")

