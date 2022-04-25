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

class H3Block(H1Block):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "### "
        self.style = pool.style_h3

class H4Block(H1Block):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "#### "
        self.style = pool.style_h4

class H5Block(H1Block):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "##### "
        self.style = pool.style_h5


class H6Block(H1Block):
    def __init__(self, pool: StylePool):
        super().__init__(pool)
        self.prefix = "###### "
        self.style = pool.style_h5

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
        print(self.prefix_size, "".join(self.buffer))

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

