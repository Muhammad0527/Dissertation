import sys
import os

# Add the python2_code directory to sys.path
current_dir = os.path.dirname(__file__)
python2_code_path = os.path.join(current_dir, '..', 'python2_code')
sys.path.insert(0, os.path.abspath(python2_code_path))

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
    lex(filename)  # Pass the filename into your lex() function
    return 0

if __name__ == "__main__":
    main(sys.argv)