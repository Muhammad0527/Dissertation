import sys

from lexer import lex

def target(driver, args):
    return main, None

def main(argv=None):
    if argv is None:
        argv = []

    if len(argv) < 2:
        print("Usage: %s <filename>" % (argv[0] if argv else "program"))
        return 1

    filename = argv[1]
    tokens = lex(filename)  
    return 0

if __name__ == "__main__":
    main(sys.argv)