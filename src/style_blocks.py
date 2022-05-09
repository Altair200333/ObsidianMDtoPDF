import math
import re
from src.styles import *

class MDBlock:
    def __init__(self, pool: StylePool):
        self.buffer = []

    def feed(self, x):
        self.buffer.append(x)

    def flush(self, pdf):
        pass

class Regex1Group(MDBlock):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.style = pool.style_normal
        self.regex = re.compile(r"(.*)", re.MULTILINE)

    def flush(self, pdf):
        buffer_text = "".join(self.buffer)

        text = buffer_text

        matches = self.regex.findall(buffer_text)

        if len(matches) > 0:
            text = matches[0]

        prev_style = pdf.text_style
        pdf.set_text_style(self.style)
       
        for x in text:
            pdf.print_char(x)

        pdf.set_text_style(prev_style)
        self.buffer = [] 
        
class H1Block(Regex1Group):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.style = pool.style_h1
        self.regex = re.compile(r"^# (.*)", re.MULTILINE)

class H2Block(Regex1Group):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.style = pool.style_h2
        self.regex = re.compile(r"^## (.*)", re.MULTILINE)

class H3Block(Regex1Group):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.style = pool.style_h3
        self.regex = re.compile(r"^### (.*)", re.MULTILINE)

class H4Block(Regex1Group):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.style = pool.style_h4
        self.regex = re.compile(r"^#### (.*)", re.MULTILINE)

class H5Block(Regex1Group):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.style = pool.style_h5
        self.regex = re.compile(r"^##### (.*)", re.MULTILINE)

class H6Block(Regex1Group):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "###### "
        self.style = pool.style_h5
        self.regex = re.compile(r"^###### (.*)", re.MULTILINE)

class MarkBlock(Regex1Group):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.style = pool.style_mark
        self.regex = re.compile(r"^[ ]*>(.*)", re.MULTILINE)

class CodeBlock(MDBlock):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "```"
        self.style = pool.style_code
        self.regex = re.compile(r"```((.|\n)*)```", re.MULTILINE)
        
    def flush(self, pdf):
        buffer_text = "".join(self.buffer)

        matches = self.regex.findall(buffer_text)
        if len(matches) < 1:
            return
        
        text = matches[0]

        prev_style = pdf.text_style
        
        pdf.set_text_style(self.style)

        start_pos = (pdf.pointer_x, pdf.pointer_y)

        for x in text:
            pdf.print_char(x)
        
        pdf.set_text_style(prev_style)
        self.buffer = []


class LinkBlock(MDBlock):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "["
        self.style = pool.style_link
        self.regex = re.compile(r"\[(.*)\]\((.*)\)", re.MULTILINE)

    def flush(self, pdf): 
        buffer_text = "".join(self.buffer)

        matches = self.regex.findall(buffer_text)
        if len(matches) < 1:
            return
        
        link_text = matches[0][0]
        link_address = matches[0][1]

        prev_style = pdf.text_style
        
        pdf.set_text_style(self.style)

        start_pos = (pdf.pointer_x, pdf.pointer_y)

        for x in link_text:
            pdf.print_char(x)
        
        width = pdf.get_string_width(link_text)
        
        pdf.set_text_style(prev_style)

        end_pos = (pdf.pointer_x, pdf.pointer_y)
        pdf.link(start_pos[0], start_pos[1], width, pdf.cell_h, link_address)

        self.buffer = []