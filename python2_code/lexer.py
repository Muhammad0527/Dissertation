# Base class for all regular expressions
class Rexp:
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.__class__.__name__

# Define various regex components as subclasses of Rexp
class ZERO(Rexp):
    pass

class ONE(Rexp):
    pass

class CHAR(Rexp):
    def __init__(self, c):
        self.c = c

    def __repr__(self):
        return "CHAR(\"%s\")" % self.c

class ALT(Rexp):
    def __init__(self, r1, r2):
        self.r1 = r1
        self.r2 = r2

    def __repr__(self):
        return "ALT(%s, %s)" % (self.r1, self.r2)

class SEQ(Rexp):
    def __init__(self, r1, r2):
        self.r1 = r1
        self.r2 = r2

    def __repr__(self):
        return "SEQ(%s, %s)" % (self.r1, self.r2)

class STAR(Rexp):
    def __init__(self, r):
        self.r = r

    def __repr__(self):
        return "STAR(%s)" % self.r

class RANGE(Rexp):
    def __init__(self, cs):
        self.cs = list(cs)

    def __repr__(self):
        return "RANGE(%s)" % self.cs

class PLUS(Rexp):
    def __init__(self, r):
        self.r = r

    def __repr__(self):
        return "PLUS(%s)" % self.r

class OPTIONAL(Rexp):
    def __init__(self, r):
        self.r = r

    def __repr__(self):
        return "OPTIONAL(%s)" % self.r

class NTIMES(Rexp):
    def __init__(self, r, n):
        self.r = r
        self.n = n

    def __repr__(self):
        return "NTIMES(%s, %d)" % (self.r, self.n)

class RECD(Rexp):
    def __init__(self, x, r):
        self.x = x
        self.r = r

    def __repr__(self):
        return "RECD(\"%s\", %s)" % (self.x, self.r)

# Values for evaluation results
class Val:
    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.__class__.__name__

class Empty(Val):
    pass

class Chr(Val):
    def __init__(self, c):
        self.c = c

    def __repr__(self):
        return "Chr(\"%s\")" % self.c

class Sequ(Val):
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

    def __repr__(self):
        return "Sequ(%s, %s)" % (self.v1, self.v2)

class Left(Val):
    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return "Left(%s)" % self.v

class Right(Val):
    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return "Right(%s)" % self.v

class Stars(Val):
    def __init__(self, vs):
        self.vs = vs

    def __repr__(self):
        return "Stars(%s)" % self.vs

class Rng(Val):
    def __init__(self, cs):
        self.cs = cs

    def __repr__(self):
        return "Rng(\"%s\")" % self.cs

class Pls(Val):
    def __init__(self, vs):
        self.vs = vs

    def __repr__(self):
        return "Pls(%s)" % self.vs

class Opt(Val):
    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return "Opt(%s)" % self.v

class Ntms(Val):
    def __init__(self, vs):
        self.vs = vs

    def __repr__(self):
        return "Ntms(%s)" % self.vs

class Rec(Val):
    def __init__(self, x, v):
        self.x = x
        self.v = v

    def __repr__(self):
        return "Rec(\"%s\", %s)" % (self.x, self.v)

def eq_rexp(r1, r2):
    # Checks whether two regular expressions r1 and r2 have the same structure
    if isinstance(r1, ZERO) and isinstance(r2, ZERO):
        return True
    if isinstance(r1, ONE) and isinstance(r2, ONE):
        return True
    if isinstance(r1, CHAR) and isinstance(r2, CHAR):
        return r1.c == r2.c
    if isinstance(r1, ALT) and isinstance(r2, ALT):
        return eq_rexp(r1.r1, r2.r1) and eq_rexp(r1.r2, r2.r2)
    if isinstance(r1, SEQ) and isinstance(r2, SEQ):
        return eq_rexp(r1.r1, r2.r1) and eq_rexp(r1.r2, r2.r2)
    if isinstance(r1, STAR) and isinstance(r2, STAR):
        return eq_rexp(r1.r, r2.r)
    if isinstance(r1, RANGE) and isinstance(r2, RANGE):
        # compare elements one by one; RPython needs simple loops
        if len(r1.cs) != len(r2.cs):
            return False
        for i in range(len(r1.cs)):
            if r1.cs[i] != r2.cs[i]:
                return False
        return True
    if isinstance(r1, PLUS) and isinstance(r2, PLUS):
        return eq_rexp(r1.r, r2.r)
    if isinstance(r1, OPTIONAL) and isinstance(r2, OPTIONAL):
        return eq_rexp(r1.r, r2.r)
    if isinstance(r1, NTIMES) and isinstance(r2, NTIMES):
        return (r1.n == r2.n) and eq_rexp(r1.r, r2.r)
    if isinstance(r1, RECD) and isinstance(r2, RECD):
        if r1.x != r2.x:
            return False
        return eq_rexp(r1.r, r2.r)

    # If none of the above matched, they're not equal structurally
    return False


def nullable(r):
    if isinstance(r, ZERO):
        return False
    elif isinstance(r, ONE):
        return True
    elif isinstance(r, CHAR):
        return False
    elif isinstance(r, ALT):
        return nullable(r.r1) or nullable(r.r2)
    elif isinstance(r, SEQ):
        return nullable(r.r1) and nullable(r.r2)
    elif isinstance(r, STAR):
        return True
    elif isinstance(r, RANGE):
        return False
    elif isinstance(r, PLUS):
        return nullable(r.r)
    elif isinstance(r, OPTIONAL):
        return True
    elif isinstance(r, NTIMES):
        if r.n == 0:
            return True
        else:
            return nullable(r.r)
    elif isinstance(r, RECD):
        return nullable(r.r)


def der(c, r):
    if isinstance(r, ZERO):
        return ZERO()
    
    elif isinstance(r, ONE):
        return ZERO()
    
    elif isinstance(r, CHAR):
        if r.c == c:
            return ONE()
        else:
            return ZERO()
    
    elif isinstance(r, ALT):
        return ALT(der(c, r.r1), der(c, r.r2))
    
    elif isinstance(r, SEQ):
        if nullable(r.r1):
            return ALT(SEQ(der(c, r.r1), r.r2), der(c, r.r2))
        else:
            return SEQ(der(c, r.r1), r.r2)
    
    elif isinstance(r, STAR):
        return SEQ(der(c, r.r), STAR(r.r))
    
    elif isinstance(r, RANGE):
        if c in r.cs:
            return ONE()
        else:
            return ZERO()
    
    elif isinstance(r, PLUS):
        return SEQ(der(c, r.r), STAR(r.r))
    
    elif isinstance(r, OPTIONAL):
        return der(c, r.r)
    
    elif isinstance(r, NTIMES):
        if r.n == 0:
            return ZERO()
        else:
            return SEQ(der(c, r.r), NTIMES(r.r, r.n - 1))
    
    elif isinstance(r, RECD):
        return der(c, r.r)
    
def regex_to_string(r):
    if isinstance(r, ZERO):
        return None
    elif isinstance(r, ONE):
        return ""
    elif isinstance(r, CHAR):
        return r.c
    elif isinstance(r, ALT):
        return "(%s | %s)" % (regex_to_string(r.r1), regex_to_string(r.r2))
    elif isinstance(r, SEQ):
        return "%s%s" % (regex_to_string(r.r1), regex_to_string(r.r2))
    elif isinstance(r, STAR):
        return "%s*" % regex_to_string(r.r)
    elif isinstance(r, RANGE):
        return "[%s]" % "".join(r.cs)
    elif isinstance(r, PLUS):
        return "%s+" % regex_to_string(r.r)
    elif isinstance(r, OPTIONAL):
        return "%s?" % regex_to_string(r.r)
    elif isinstance(r, NTIMES):
        return "%s{%d}" % (regex_to_string(r.r), r.n)
    elif isinstance(r, RECD):
        return "%s" % regex_to_string(r.r)

def ders(r, s):
    if not s:
        return r
    else:
        return ders(der(s[0], r), s[1:])
    
def size(r):
    if isinstance(r, ZERO) or isinstance(r, ONE):
        return 1
    elif isinstance(r, CHAR):
        return 1
    elif isinstance(r, ALT):
        return 1 + size(r.r1) + size(r.r2)
    elif isinstance(r, SEQ):
        return 1 + size(r.r1) + size(r.r2)
    elif isinstance(r, STAR):
        return 1 + size(r.r)
    elif isinstance(r, RANGE):
        return 1
    elif isinstance(r, PLUS):
        return 1 + size(r.r)
    elif isinstance(r, OPTIONAL):
        return 1 + size(r.r)
    elif isinstance(r, NTIMES):
        return 1 + size(r.r)
    elif isinstance(r, RECD):
        return 1 + size(r.r)

# Flatten function to convert a value to a string
def flatten(v):
    if isinstance(v, Empty):
        return ""
    elif isinstance(v, Chr):
        return v.c
    elif isinstance(v, Left):
        return flatten(v.v)
    elif isinstance(v, Right):
        return flatten(v.v)
    elif isinstance(v, Sequ):
        return flatten(v.v1) + flatten(v.v2)
    elif isinstance(v, Stars):
        result = ""
        for val in v.vs:
            result += flatten(val)
        return result
    elif isinstance(v, Rng):
        result = ""
        for c in v.cs:
            if isinstance(c, Chr):
                result += c.c
        return result
    elif isinstance(v, Pls):
        result = ""
        for val in v.vs:
            result += flatten(val)
        return result
    elif isinstance(v, Opt):
        return flatten(v.v)
    elif isinstance(v, Ntms):
        result = ""
        for val in v.vs:
            result += flatten(val)
        return result
    elif isinstance(v, Rec):
        return flatten(v.v)

def env(v):
    if isinstance(v, Empty):
        return []
    
    elif isinstance(v, Chr):
        # Characters alone do not produce environment bindings
        return []
    
    elif isinstance(v, Left):
        return env(v.v)
    
    elif isinstance(v, Right):
        return env(v.v)
    
    elif isinstance(v, Sequ):
        # Concatenate results from both parts of the sequence
        return env(v.v1) + env(v.v2)
    
    elif isinstance(v, Stars):
        # Collect results from each value in the list of stars
        result = []
        for val in v.vs:
            result += env(val)
        return result
    
    elif isinstance(v, Rng):
        # Range does not produce bindings directly
        return []
    
    elif isinstance(v, Pls):
        # Collect results from each value in the list of plus expressions
        result = []
        for val in v.vs:
            result += env(val)
        return result
    
    elif isinstance(v, Opt):
        # Optional expression contributes bindings if it has content
        return env(v.v)
    
    elif isinstance(v, Ntms):
        # Collect results from each value in the list of n-times expressions
        result = []
        for val in v.vs:
            result += env(val)
        return result
    
    elif isinstance(v, Rec):
        # Captured expressions produce a binding with their name and value
        return [(v.x, flatten(v.v))] + env(v.v)

def mkeps(r):
    if isinstance(r, ONE):
        return Empty()
    
    elif isinstance(r, ALT):
        if nullable(r.r1):
            return Left(mkeps(r.r1))
        else:
            return Right(mkeps(r.r2))
    
    elif isinstance(r, SEQ):
        return Sequ(mkeps(r.r1), mkeps(r.r2))
    
    elif isinstance(r, STAR):
        return Stars([])
    
    elif isinstance(r, PLUS):
        return Pls([mkeps(r.r)])
    
    elif isinstance(r, OPTIONAL):
        return Opt((Empty()))
    
    elif isinstance(r, NTIMES):
        if r.n == 0:
            return Ntms(list())
        
        return Ntms([mkeps(r.r)])
    
    elif isinstance(r, RECD):
        return Rec(r.x, mkeps(r.r))

def inj(r, c, v):
    if isinstance(r, STAR) and isinstance(v, Sequ):
        # STAR: add the injected value to the list in Stars
        return Stars([inj(r.r, c, v.v1)] + v.v2.vs)
    
    elif isinstance(r, SEQ):
        # SEQ: inject the character into the first part if possible
        if isinstance(v, Sequ):
           return Sequ(inj(r.r1, c, v.v1), v.v2)
        elif isinstance(v, Left):  # When SEQ has nullable first part
            return Sequ(inj(r.r1, c, v.v.v1), v.v.v2)
        elif isinstance(v, Right):
            return Sequ(mkeps(r.r1), inj(r.r2, c, v.v))
    
    elif isinstance(r, ALT):
        # ALT: inject into the Left or Right based on the value type
        if isinstance(v, Left):
            return Left(inj(r.r1, c, v.v))
        elif isinstance(v, Right):
            return Right(inj(r.r2, c, v.v))
    
    elif isinstance(r, CHAR):
        # CHAR: represent the character with a Chr value
        return Chr(c)
    
    # New cases for the extended regular expressions:
    
    elif isinstance(r, RANGE):
        # RANGE: simply return the character as Chr if it matches
        return Chr(c)
    
    elif isinstance(r, PLUS):
        # PLUS: inject into the repeated part and add it to Pls list
        if isinstance(v, Sequ):
            return Pls([inj(r.r, c, v.v1)] + v.v2.vs)
    
    elif isinstance(r, OPTIONAL):
        # OPTIONAL: wrap the injected character in Opt
        return Opt(inj(r.r, c, v))
    
    elif isinstance(r, NTIMES):
        # NTIMES: inject into the specified number of times
        if isinstance(v, Sequ):
            return Ntms([inj(r.r, c, v.v1)] + v.v2.vs)
    
    elif isinstance(r, RECD):
        # RECD: inject within the recorded regular expression
        return Rec(r.x, inj(r.r, c, v))

# Functions translated to RPython
def F_ID(v):
    return v

def F_RIGHT(f):
    def result(v):
        return Right(f(v))
    return result

def F_LEFT(f):
    def result(v):
        return Left(f(v))
    return result

def F_ALT(f1, f2):
    def result(v):
        if isinstance(v, Right):
            return Right(f2(v.v))
        elif isinstance(v, Left):
            return Left(f1(v.v))
        else:
            raise Exception("Invalid type for F_ALT")
    return result

def F_SEQ(f1, f2):
    def result(v):
        if isinstance(v, Sequ):
            return Sequ(f1(v.v1), f2(v.v2))
        else:
            raise Exception("Invalid type for F_SEQ")
    return result

def F_SEQ_Empty1(f1, f2):
    def result(v):
        return Sequ(f1(Empty()), f2(v))
    return result

def F_SEQ_Empty2(f1, f2):
    def result(v):
        return Sequ(f1(v), f2(Empty()))
    return result

def F_RECD(f):
    def result(v):
        if isinstance(v, Rec):
            return Rec(v.x, f(v.value))
        else:
            raise Exception("Invalid type for F_RECD")
    return result

def F_ERROR(v):
    raise Exception("error")

def simp(r):
    if isinstance(r, ALT):
        # Recursively simplify ALT components
        r1s, f1s = simp(r.r1)
        r2s, f2s = simp(r.r2)
        if isinstance(r1s, ZERO):
            return r2s, F_RIGHT(f2s)
        elif isinstance(r2s, ZERO):
            return r1s, F_LEFT(f1s)
        elif eq_rexp(r1s, r2s):
            return r1s, F_LEFT(f1s)
        else:
            return ALT(r1s, r2s), F_ALT(f1s, f2s)

    elif isinstance(r, SEQ):
        # Recursively simplify SEQ components
        r1s, f1s = simp(r.r1)
        r2s, f2s = simp(r.r2)
        if isinstance(r1s, ZERO) or isinstance(r2s, ZERO):
            return ZERO(), F_ERROR
        elif isinstance(r1s, ONE):
            return r2s, F_SEQ_Empty1(f1s, f2s)
        elif isinstance(r2s, ONE):
            return r1s, F_SEQ_Empty2(f1s, f2s)
        else:
            return SEQ(r1s, r2s), F_SEQ(f1s, f2s)

    else:
        # For other types, return as is with F_ID
        return (r, F_ID)

def lex_simp(r, s):
    if not s:  # If the list is empty
        if nullable(r):
            return mkeps(r)
        else:
            raise Exception("lexing error") 
    else:
        c, cs = s[0], s[1:]
        r_simp, f_simp = simp(der(c, r))  # Calculate the derivative and simplify
        return inj(r, c, f_simp(lex_simp(r_simp, cs)))  # Recursively call lex_simp

def lexing_simp(r, s):
    return env(lex_simp(r, list(s)))

# Define regex for keywords in language
while_regex = SEQ(CHAR("w"), SEQ(CHAR("h"), SEQ(CHAR("i"), SEQ(CHAR("l"), CHAR("e")))))
if_regex = SEQ(CHAR("i"), CHAR("f"))
then_regex = SEQ(CHAR("t"), SEQ(CHAR("h"), SEQ(CHAR("e"), CHAR("n"))))
else_regex = SEQ(CHAR("e"), SEQ(CHAR("l"), SEQ(CHAR("s"), CHAR("e"))))
do_regex = SEQ(CHAR("d"), CHAR("o"))
true_regex = SEQ(CHAR("t"), SEQ(CHAR("r"), SEQ(CHAR("u"), CHAR("e"))))
false_regex = SEQ(CHAR("f"), SEQ(CHAR("a"), SEQ(CHAR("l"), SEQ(CHAR("s"), CHAR("e")))))
read_regex = SEQ(CHAR("r"), SEQ(CHAR("e"), SEQ(CHAR("a"), CHAR("d"))))
write_regex = SEQ(CHAR("w"), SEQ(CHAR("r"), SEQ(CHAR("i"), SEQ(CHAR("t"), CHAR("e")))))
skip_regex = SEQ(CHAR("s"), SEQ(CHAR("k"), SEQ(CHAR("i"), CHAR("p"))))

KEYWORD_REGEX = ALT(while_regex, ALT(if_regex, ALT(then_regex, ALT(else_regex, ALT(true_regex, ALT(false_regex, ALT(read_regex, ALT(write_regex, ALT(do_regex, skip_regex)))))))))

# Define regex for operations in language
plus_regex = CHAR("+")
minus_regex = CHAR("-")
times_regex = CHAR("*")
modulus_regex = CHAR("%")
divide_regex = CHAR("/")
equality_regex = SEQ(CHAR("="), CHAR("="))
not_equal_regex = SEQ(CHAR("!"), CHAR("="))
greater_than_regex = CHAR(">")
less_than_regex = CHAR("<")
less_than_equal_regex = SEQ(CHAR("<"), CHAR("="))
greater_than_equal_regex = SEQ(CHAR(">"), CHAR("="))
assign_regex = SEQ(CHAR(":"), CHAR("="))
and_regex = SEQ(CHAR("&"), CHAR("&"))
or_regex = SEQ(CHAR("|"), CHAR("|"))

OPERATORS_REGEX = ALT(plus_regex, ALT(minus_regex, ALT(times_regex, ALT(divide_regex, ALT(modulus_regex, ALT(equality_regex, ALT(not_equal_regex, ALT(less_than_regex, ALT(greater_than_regex, ALT(less_than_equal_regex, ALT(greater_than_equal_regex, ALT(assign_regex, ALT(and_regex, or_regex)))))))))))))

# Define regex for letters in language
LETTERS_REGEX = RANGE("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Define regex for symbols in language
full_stop_regex = CHAR(".")
underscore_regex = CHAR("_")
equal_regex = CHAR("=")
semicolon_regex = CHAR(";")
comma_regex = CHAR(",")
backslash_regex = CHAR("\\")
colon_regex = CHAR(":")

SYMBOLS_REGEX = ALT(backslash_regex, ALT(comma_regex, ALT(semicolon_regex, ALT(colon_regex, ALT(underscore_regex, ALT(full_stop_regex, ALT(less_than_regex, ALT(greater_than_regex, ALT(LETTERS_REGEX, equal_regex)))))))))

# Define regex for parentheses in language
left_parenthesis_regex = CHAR("(")
right_parenthesis_regex = CHAR(")")
left_brace_regex = CHAR("{")
right_brace_regex = CHAR("}")

PARENTHESES_REGEX = ALT(left_parenthesis_regex, ALT(right_parenthesis_regex, ALT(left_brace_regex, right_brace_regex)))

# Define regex for numbers in language
DIGITS_REGEX = RANGE("0123456789")

# Define regex for whitespace in language
WHITESPACE_REGEX = PLUS(RANGE(" \t\n"))

# Define regex for identifiers in language
IDENTIFIER_REGEX = SEQ(LETTERS_REGEX, STAR(ALT(LETTERS_REGEX, ALT(DIGITS_REGEX, underscore_regex))))

# Define regex for numbers in language
natual_numbers_regex = RANGE("123456789")

NUMBERS_REGEX = ALT(CHAR("0"), SEQ(natual_numbers_regex, STAR(DIGITS_REGEX)))

# Define regex for strings in language
speech_mark_regex = CHAR("\"")
newline_regex = SEQ(CHAR("\\"), CHAR("n"))

STRING_REGEX = SEQ(speech_mark_regex, SEQ(STAR(ALT(SYMBOLS_REGEX, ALT(DIGITS_REGEX, ALT(PARENTHESES_REGEX, ALT(WHITESPACE_REGEX, newline_regex))))), speech_mark_regex))

# Define regex for commennts in language
forward_slashs_regex = SEQ(CHAR("/"), CHAR("/"))

COMMENT_REGEX = SEQ(forward_slashs_regex, SEQ(STAR(ALT(SYMBOLS_REGEX, ALT(CHAR(" "), ALT(PARENTHESES_REGEX, DIGITS_REGEX)))), CHAR("\n")))

# Define records for the whole language
KEYWORD_RECORD = RECD("k", KEYWORD_REGEX)
OPERATORS_RECORD = RECD("o", OPERATORS_REGEX)
STRING_RECORD = RECD("str", STRING_REGEX)
PARANTHESES_RECORD = RECD("p", PARENTHESES_REGEX)
SEMICOLON_RECORD = RECD("s", semicolon_regex)
WHITESPACE_RECORD = RECD("w", WHITESPACE_REGEX)
IDENTIFIER_RECORD = RECD("i", IDENTIFIER_REGEX)
NUMBERS_RECORD = RECD("n", NUMBERS_REGEX)
COMMENTS_RECORD = RECD("c", COMMENT_REGEX)

# Define regex for the whole language
LANGUAGE_REGEX = STAR(ALT(KEYWORD_RECORD, ALT(OPERATORS_RECORD, ALT(STRING_RECORD, ALT(PARANTHESES_RECORD, ALT(SEMICOLON_RECORD, ALT(WHITESPACE_RECORD, ALT(IDENTIFIER_RECORD, ALT(NUMBERS_RECORD, COMMENTS_RECORD)))))))))

# Tokens
class Token:

    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return self.__class__.__name__
    
    def __eq__(self, other):
        return self.__dict__ == other.__dict__
    
    def __hash__(self):
        return hash(tuple(sorted(self.__dict__.items())))

class T_KEYWORD(Token):
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "T_KEYWORD(%s)" % self.s

class T_OP(Token):
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "T_OP(%s)" % self.s

class T_STRING(Token):
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "T_STRING(%s)" % self.s

class T_PAREN(Token):
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "T_PAREN(%s)" % self.s

class T_SEMI(Token):
    def __init__(self):
        pass

class T_ID(Token):
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "T_ID(%s)" % self.s

class T_NUM(Token):
    def __init__(self, n):
        self.n = int(n)  # Ensure integer conversion

    def __repr__(self):
        return "T_NUM(%d)" % self.n


def token(pair):
    kind, value = pair
    if kind == "k":
        return T_KEYWORD(value)
    elif kind == "o":
        return T_OP(value)
    elif kind == "str":
        return T_STRING(value)
    elif kind == "p":
        return T_PAREN(value)
    elif kind == "s":
        return T_SEMI()  # No argument, singleton class
    elif kind == "i":
        return T_ID(value)
    elif kind == "n":
        return T_NUM(value)  # Convert to integer
    else:
        return None


def tokenise(s):
    lexed = lexing_simp(LANGUAGE_REGEX, s)
    result = []
    for pair in lexed:
        tk = token(pair)
        if tk != None:
            result.append(tk)
    return result  # Return list of Token objects

# This code will not run in RPython, only used to test the tokenise function

import os
import time

def read_file(file):
    """Reads the content of a file from the 'examples' directory."""
    path = os.path.join(os.getcwd(), "examples", file)
    with open(path, "r") as f:
        return f.read()

def test(file):
    contents = read_file(file)
    print("Lex " + file + ": ")
    start = time.time()
    print(tokenise(contents))
    end = time.time()

    print("Time taken: " + str(end - start) + " seconds")

if __name__ == "__main__":
    filename = raw_input("Enter filename: ")  # For Python 2 / RPython
    test(filename)