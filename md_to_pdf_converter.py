import numpy as np
from PIL import Image
import re
from css_parser import *
from fpdf import FPDF
from color_utils import *
import os.path
from fpdf_extention import *


def read_contents(path):
    input_file = path
    file = open(input_file,encoding = 'utf-8',mode =  "r")
    file_text = file.read()
    file.close()
    return file_text

def convert_md(file_text, pdf: PrintablePDF, blocks, pool: StylePool):
    """
    Prints provided markdown file to PDF using mardkown blocks
    """
    char_buffer = []
    regular_buffer = []
    active_block = None

    pdf.add_page()
    pdf.set_text_style(pool.style_normal)

    for x in file_text:

        char_buffer.append(x)

        if active_block is None:
            regular_buffer.append(x)

            for block in blocks:
                found = False
                if not found and block.is_start(char_buffer):
                    block.start(char_buffer)
        
                    regular_buffer = regular_buffer[:-block.get_prefix_size()]
                    for letter in regular_buffer:
                        pdf.print_char(letter)

                    regular_buffer = []

                    active_block = block
                    found = True
        else:
            if active_block.is_end(char_buffer):
                if x == '\n':
                    regular_buffer.append(x)
                else:
                    active_block.feed(x)

                active_block.flush(pdf)
                active_block = None
                #print(counter, " is end")
            else:
                active_block.feed(x)

    for letter in regular_buffer:
        pdf.print_char(letter)
    pdf.finish_print()