import re
from src.styles import *

class MDBlock:
    def __init__(self, pool: StylePool):
        self.buffer = []

    def is_start(self, buffer) -> bool:
        pass
    def is_end(self, buffer) -> bool:
        pass
    def start(self, regular_buffer):
        self.buffer = []
    def get_prefix_size(self) -> int:
        pass
    
    def feed(self, x):
        self.buffer.append(x)

    def flush(self, pdf):
        pass

class H1Block(MDBlock):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "# "
        self.style = pool.style_h1
        self.regex = re.compile(r"^# (.*)", re.MULTILINE)

    def is_start(self, buffer):
        last_simbols = buffer[-len(self.prefix):]

        return "".join(last_simbols) == self.prefix and (len(buffer) == len(self.prefix) or buffer[-len(self.prefix) - 1] == '\n')

    def is_end(self, buffer):
        return buffer[-1] == '\n'
    
    def get_prefix_size(self):
        return len(self.prefix)

    def flush(self, pdf):
        #regular = "".join(self.buffer)
        #print("H: ", regular)

        prev_style = pdf.text_style
        pdf.set_text_style(self.style)
        for x in self.buffer:
            pdf.print_char(x)
        pdf.set_text_style(prev_style)
        self.buffer = []

class H2Block(H1Block):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "## "
        self.style = pool.style_h2
        self.regex = re.compile(r"^## (.*)", re.MULTILINE)

class H3Block(H1Block):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "### "
        self.style = pool.style_h3
        self.regex = re.compile(r"^### (.*)", re.MULTILINE)

class H4Block(H1Block):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "#### "
        self.style = pool.style_h4
        self.regex = re.compile(r"^#### (.*)", re.MULTILINE)

class H5Block(H1Block):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "##### "
        self.style = pool.style_h5
        self.regex = re.compile(r"^##### (.*)", re.MULTILINE)

class H6Block(H1Block):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "###### "
        self.style = pool.style_h5
        self.regex = re.compile(r"^###### (.*)", re.MULTILINE)

class MarkBlock(MDBlock):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = ">"
        self.style = pool.style_mark
        self.prefix_size = len(self.prefix)

    def is_start(self, buffer):
        last_simbols = buffer[-len(self.prefix):]
        
        if "".join(last_simbols) == self.prefix:
            all_spaces = True
            for i in reversed(range(len(buffer) -1)):
                x = buffer[i]
                if x == '\n':
                    break
                elif x != ' ' and x != '\t':
                    all_spaces = False

            if all_spaces:
                return True

        return False

    def start(self, regular_buffer):
        super().start(regular_buffer)
        
        self.prefix_size = 0

        for i in reversed(range(len(regular_buffer))):
            x = regular_buffer[i]
            if x == '\n':
                break

            self.prefix_size += 1

        self.buffer = regular_buffer[-self.prefix_size:-1]
        #print(self.prefix_size, "".join(self.buffer))

    def is_end(self, buffer):
        return buffer[-1] == '\n'
    
    def get_prefix_size(self):
        return self.prefix_size

    def flush(self, pdf):
        #regular = "".join(self.buffer)
        #print("H: ", regular)

        prev_style = pdf.text_style
        pdf.set_text_style(self.style)
        for x in self.buffer:
            pdf.print_char(x)
        pdf.set_text_style(prev_style)
        self.buffer = []

class CodeBlock(MDBlock):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "```"
        self.style = pool.style_code
        
    def is_start(self, buffer):
        last_simbols = buffer[-len(self.prefix):]

        return "".join(last_simbols) == self.prefix

    def is_end(self, buffer):
        last_simbols = buffer[-len(self.prefix):]
        return "".join(last_simbols) == self.prefix
    
    def get_prefix_size(self):
        return len(self.prefix)

    def flush(self, pdf):
        #regular = "".join(self.buffer)
        #print("H: ", regular)

        self.buffer = self.buffer[:-self.get_prefix_size()]
        prev_style = pdf.text_style
        pdf.set_text_style(self.style)
        for x in self.buffer:
            pdf.print_char(x)
        pdf.set_text_style(prev_style)
        self.buffer = []


class LinkBlock(MDBlock):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "["
        self.style = pool.style_link
        self.regex = re.compile(r"\[(.*)\]\((.*)\)")

    def is_start(self, buffer):
        last_simbols = buffer[-len(self.prefix):]

        return "".join(last_simbols) == self.prefix

    def is_end(self, buffer):
        buffer_text = "".join(buffer)
        matches = self.regex.findall(buffer_text)

        return len(matches) > 0
    
    def get_prefix_size(self):
        return len(self.prefix)

    def start(self, regular_buffer):
        self.buffer = regular_buffer[-self.get_prefix_size():]

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