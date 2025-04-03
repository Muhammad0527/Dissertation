import sys
import os

from lexer import lex
from parser import parse_program
#from recursive_eval import run
from iterative_eval import run

def read_file(file):
    """Reads the content of a file from the 'examples' directory."""
    path = os.path.join(os.getcwd(), "examples", file)
    with open(path, "r") as f:
        return f.read()

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