
def rgb_to_hex(vals):
    if len(vals)!=3 and len(vals)!=4:
        raise Exception("RGB or RGBA inputs to RGBtoHex must have three or four elements!")
    
    #Ensure values are rounded integers, convert to hex, and concatenate
    return '#'+ ''.join(['{:02X}'.format(int(x)) for x in vals])

def hex_to_rgba(color):
    value = color.replace('#','')

    if len(value)!=6 and len(value)!=8:
        raise Exception("RGB or RGBA inputs to RGBtoHex must have six or eight elements!")
    if len(value) == 6:
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))
    else:
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4, 6))