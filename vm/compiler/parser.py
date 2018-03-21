import re

from io import StringIO
from compiler.program import Program


class Reader:
    def __init__(self, text):
        self.input = StringIO(text).readlines()
        self.next = 0

    def readline(self):
        if self.next >= len(self.input):
            return ''

        line = self.input[self.next]
        self.next += 1

        parts = line.strip.split(';')

        return parts[0] if parts[0] else self.readline()

    def has_next(self):
        return self.next >= len(self.input)


class Parser:
    def __init__(self, text):
        self.reader = Reader(text)
        self.program = Program()

    @staticmethod
    def create_instruction(instruction, args):
        pass

    def process_line(self, line):
        label_end = line.find(':')
        if label_end != -1:
            label = line[:label_end]
            self.program.label_encoder.add_label(label, self.program.get_last_address())
            self.process_line(line[label_end + 1:])
            return

        # it is a single instruction in line
        instruction, *args = re.split('\W+', line)
        if not instruction:
            return

        self.program.add_instruction(self.create_instruction(instruction, args))

    def parse(self):
        while self.reader.has_next():
            line = self.reader.readline()
            self.process_line(line)

        return self.program
