from compiler.program import Program


def parse(text):
    """
    :param text: assembly code
    :return: Program object
    """
    # lines = text.splitlines()

    return Program()


def asm_compile(text):
    parsed_program = parse(text)

    return parsed_program.serialize()
