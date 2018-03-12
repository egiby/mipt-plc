from compilator import asm_compile

import sys

from argparse import ArgumentParser


def parse_args(argv):
    argument_parser = ArgumentParser()
    argument_parser.add_argument('code', help='input compilator path')
    argument_parser.add_argument('--output', '-o', help='output binary path', default='a.out')

    return argument_parser.parse_args(argv)


def main(args):
    with open(args.code) as code_file:
        text = code_file.read()
        binary = asm_compile(text)
        with open(args.output, 'wb') as out:
            out.write(binary)


if __name__ == '__main__':
    main(parse_args(sys.argv[1:]))
