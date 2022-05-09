import re
import numpy as np
from src.css.color_utils import *

def read_css(path):
    file = open(path, mode='r')

    # read all lines at once
    css_file = file.read()

    file.close()

    return css_file

'''Returns css block with spicified title encosed by curly brackets '''
def find_block(string, name):
    regex_string = name + r"[^{]*[{][^{]*[}]"
    
    match = re.findall(regex_string, string)
    
    if match is not None and len(match) > 0:
        return match
    
    print(name + " not found in input string")
    return None


def get_values_dict(colors_block):
    regex_string = r"(--[a-zA-Z0-9\-]*)[:]([^;]*)" #r"(--[^:]*)[:]([^;]*)"
    mathes = re.findall(regex_string, colors_block)
    #print(mathes)
    colors_dict = {}

    for key, color in mathes:
        colors_dict[key] = color.replace(' ','')

    return colors_dict

@np.vectorize
def percents_to_number(value, max = 255):
    matches = re.findall(r"\d*%", value)

    for match in matches:
        fraction = float(match.replace("%", ""))
        value = value.replace(match, str(int(max * fraction * 0.01)))
    return value

@np.vectorize
def fraction_to_int(value, max = 255):
    matches = re.findall(r"\d*[.]\d", value)

    for match in matches:
        fraction = float(match)
        if fraction <= 1.0:
            value = value.replace(match, str(int(max * fraction)))
        else:
            value = value.replace(match, str(int(fraction)))

    return value

def look_up_values(value, colors_dict):
    match_var = r"(var\((--[^)]*)\))"

    # look up nested references *angry preprocessor sounds*
    found = True
    while found:
        found = False

        matches = re.findall(match_var, value)
        

        for match in matches:
            to_replace = match[0]
            variable = match[1]

            if variable in colors_dict:
                value = value.replace(to_replace, colors_dict[variable])
                found = True

    return value

def replace_hex(value, regex):
    matches = re.findall(regex, value)
    for match in matches:
        arguments = fraction_to_int(match[1:], 255)
        arguments = percents_to_number(arguments, 255)

        hex = rgb_to_hex(arguments)
        value = hex

    return value


def convert_rgb_to_hex(value):
    match_var = r"(rgba\(([^,]*),([^,]*),([^,]*),([^)]*))"

    value = replace_hex(value, match_var)
    
    match_var = r"(rgb\(([^,]*),([^,]*),([^)]*))"

    value = replace_hex(value, match_var)

    return value

def deduce_color_value(value, colors_dict):
    value = value.replace(' ', '')

    value = look_up_values(value, colors_dict)

    value = convert_rgb_to_hex(value)
    
    return value

def get_theme_colors(theme, colors_dict):
    output = {}
    
    for name, value in theme.items():
        deduced = deduce_color_value(value, colors_dict)
        output[name] = deduced
    
    return output

def get_theme_colors(colors_dict):
    output = {}
    
    for name, value in colors_dict.items():
        deduced = deduce_color_value(value, colors_dict)
        output[name] = deduced
    
    return output

def get_theme_from_file(path, theme = "dark"):
    css_file = read_css(path)

    blocks = find_block(css_file, "")

    light_theme_name = ".theme-light"
    dark_theme_name = ".theme-dark"

    general_blocks = []
    ligt_theme_blocks = []
    dark_theme_blocks = []

    for block in blocks:
        if dark_theme_name in block:
            dark_theme_blocks.append(block)
        elif light_theme_name in block:
            ligt_theme_blocks.append(block)
        else:
            general_blocks.append(block)

    used_theme_blocks = dark_theme_blocks if theme == "dark" else ligt_theme_blocks
    global_block_list = []

    for block in general_blocks:
        global_block_list.append(block)
        
    for block in used_theme_blocks:
        global_block_list.append(block) 

    styles = "\n".join(global_block_list)
    values_dict = get_values_dict(styles)
    colors_dict = get_theme_colors(values_dict)

    return colors_dict