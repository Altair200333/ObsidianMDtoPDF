import numpy as np
from PIL import Image
import re
from src.css.css_parser import *
from fpdf import FPDF
from src.css.color_utils import *
import os.path
from src.fpdf_extention import *
from src.style_blocks import *


def read_contents(path):
    input_file = path
    file = open(input_file,encoding = 'utf-8',mode =  "r")
    file_text = file.read()
    file.close()
    return file_text

def convert_md_to_pdf(file_text, pdf: PrintablePDF, pool: StylePool):
    """
    Prints provided markdown file to PDF using mardkown blocks
    """

    #supported style blocks
    blocks = [H1Block(pool), H2Block(pool), H3Block(pool), H4Block(pool), H5Block(pool), H6Block(pool), MarkBlock(pool), CodeBlock(pool), LinkBlock(pool)]

    char_buffer = []
    regular_buffer = []
    active_block = None
    
    pdf.set_doc_style(pool.doc_style)

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


    def import_obsidian_styles():
        pass