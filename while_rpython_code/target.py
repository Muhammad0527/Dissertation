import sys
import os

from lexer import lex
from parser import parse_program
from iterative_jit import run

def read_file(file):
    cwd = os.getcwd()
    path = os.path.join(os.path.join(cwd, "examples"), file)
    f = open(path, "r")
    content = f.read()
    f.close()
    return content

def target(driver, args):
    return main, None

def main(argv=None):
    if argv is None:
        argv = []

    if len(argv) < 2:
        print("Usage: %s <filename>" % (argv[0] if argv else "program"))
        return 1

    filename = argv[1]
    contents = read_file(filename)
    tokens = lex(contents)
    ast = parse_program(tokens)
    run(ast)
    return 0

if __name__ == "__main__":
    main(sys.argv)


def jitpolicy(driver):
    from rpython.jit.codewriter.policy import JitPolicy
    return JitPolicy()