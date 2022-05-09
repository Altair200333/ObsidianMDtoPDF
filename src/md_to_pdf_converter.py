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

# mark end and start of each md block in table
def mark_block(block, id, table, string):
    results = [(m.start(0), m.end(0)) for m in block.regex.finditer(string)]
    for res in results:
        table[res[0]] = id
        table[res[1]] = -id

def convert_md_to_pdf(file_text, pdf: PrintablePDF, pool: StylePool):
    """
    Prints provided markdown file to PDF using mardkown blocks
    """
    pdf.set_doc_style(pool.doc_style)

    pdf.add_page()
    pdf.set_text_style(pool.style_normal)

    #supported style blocks
    blocks = [H1Block(pool), H2Block(pool), H3Block(pool), H4Block(pool), H5Block(pool), H6Block(pool), MarkBlock(pool), CodeBlock(pool), LinkBlock(pool)]

    style_dict = {}

    for i, block in enumerate(blocks):
        mark_block(block, i + 1, style_dict, file_text)

    style_stack = []

    current_style = None
    for i, c in enumerate(file_text):
        if i in style_dict:
            value = style_dict[i]
            if value > 0:
                if current_style is not None:
                    current_style.flush(pdf)
                
                style_stack.append(value)
                current_style = blocks[abs(value) - 1]
                current_style.feed(c)

            if value < 0:
                style_stack.pop()
                current_style.feed(c)
                current_style.flush(pdf)
                current_style = None

                pdf.print_char(c)
                
                # if there is was style before this make it the main one
                if len(style_stack) > 0:
                    last_id = style_stack[-1] - 1
                    current_style = blocks[last_id]
                
        else:
            # no style - normal text
            if current_style == None:
                pdf.print_char(c)
            else:
                current_style.feed(c)

    pdf.finish_print()

def import_obsidian_styles(styles_path):
    colors = get_theme_from_file(styles_path)

    pool = StylePool()
    pool.doc_style.set_background_color(colors["--background-primary"])
    pool.style_normal.set_font_color(colors["--text-normal"])

    pool.style_h1.set_font_color(colors["--text-title-h1"])
    pool.style_h2.set_font_color(colors["--text-title-h2"])
    pool.style_h3.set_font_color(colors["--text-title-h3"])
    pool.style_h4.set_font_color(colors["--text-title-h4"])
    pool.style_h5.set_font_color(colors["--text-title-h5"])
    pool.style_h6.set_font_color(colors["--text-title-h6"])

    pool.style_code.set_font_color(colors["--code-block"])
    pool.style_code.set_background_color(colors["--pre-code"])

    pool.style_mark.set_font_color(colors["--text-normal"])
    pool.style_mark.set_background_color(colors["--pre-code"])

    pool.style_link.set_font_color(colors["--text-accent"])

    return pool