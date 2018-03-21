from compiler.program import Program
from compiler.parser import Parser


def parse(text):
    """
    :param text: assembly code
    :return: Program object
    """
    code_parser = Parser(text)
    return code_parser.parse()


def asm_compile(text):
    parsed_program = parse(text)

    return parsed_program.serialize()
