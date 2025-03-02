# -*- coding: utf-8 -*-
"""
RPython-compatible lexer code for the WHILE language.
Note: All classes that hold instance attributes now define __slots__.
"""

class Rexp:
    __slots__ = ()  # No instance attributes in base class

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.__class__.__name__

# Define various regex components as subclasses of Rexp
class ZERO(Rexp):
    __slots__ = ()

class ONE(Rexp):
    __slots__ = ()

class CHAR(Rexp):
    __slots__ = ('c',)
    def __init__(self, c):
        self.c = c
    def __repr__(self):
        return "CHAR(\"%s\")" % self.c

class ALT(Rexp):
    __slots__ = ('r1', 'r2')
    def __init__(self, r1, r2):
        self.r1 = r1
        self.r2 = r2
    def __repr__(self):
        return "ALT(%s, %s)" % (self.r1, self.r2)

class SEQ(Rexp):
    __slots__ = ('r1', 'r2')
    def __init__(self, r1, r2):
        self.r1 = r1
        self.r2 = r2
    def __repr__(self):
        return "SEQ(%s, %s)" % (self.r1, self.r2)

class STAR(Rexp):
    __slots__ = ('r',)
    def __init__(self, r):
        self.r = r
    def __repr__(self):
        return "STAR(%s)" % self.r

class RANGE(Rexp):
    __slots__ = ('cs',)
    def __init__(self, cs):
        self.cs = list(cs)
    def __repr__(self):
        return "RANGE(%s)" % self.cs

class PLUS(Rexp):
    __slots__ = ('r',)
    def __init__(self, r):
        self.r = r
    def __repr__(self):
        return "PLUS(%s)" % self.r

class OPTIONAL(Rexp):
    __slots__ = ('r',)
    def __init__(self, r):
        self.r = r
    def __repr__(self):
        return "OPTIONAL(%s)" % self.r

class NTIMES(Rexp):
    __slots__ = ('r', 'n')
    def __init__(self, r, n):
        self.r = r
        self.n = n
    def __repr__(self):
        return "NTIMES(%s, %d)" % (self.r, self.n)

class RECD(Rexp):
    __slots__ = ('x', 'r')
    def __init__(self, x, r):
        self.x = x
        self.r = r
    def __repr__(self):
        return "RECD(\"%s\", %s)" % (self.x, self.r)

# Values for evaluation results
class Val:
    __slots__ = ()
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.__class__.__name__

class Empty(Val):
    __slots__ = ()

class Chr(Val):
    __slots__ = ('c',)
    def __init__(self, c):
        self.c = c
    def __repr__(self):
        return "Chr(\"%s\")" % self.c

class Sequ(Val):
    __slots__ = ('v1', 'v2')
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2
    def __repr__(self):
        return "Sequ(%s, %s)" % (self.v1, self.v2)

class Left(Val):
    __slots__ = ('v',)
    def __init__(self, v):
        self.v = v
    def __repr__(self):
        return "Left(%s)" % self.v

class Right(Val):
    __slots__ = ('v',)
    def __init__(self, v):
        self.v = v
    def __repr__(self):
        return "Right(%s)" % self.v

class Stars(Val):
    __slots__ = ('vs',)
    def __init__(self, vs):
        self.vs = vs
    def __repr__(self):
        return "Stars(%s)" % self.vs

class Rng(Val):
    __slots__ = ('cs',)
    def __init__(self, cs):
        self.cs = cs
    def __repr__(self):
        return "Rng(\"%s\")" % self.cs

class Pls(Val):
    __slots__ = ('vs',)
    def __init__(self, vs):
        self.vs = vs
    def __repr__(self):
        return "Pls(%s)" % self.vs

class Opt(Val):
    __slots__ = ('v',)
    def __init__(self, v):
        self.v = v
    def __repr__(self):
        return "Opt(%s)" % self.v

class Ntms(Val):
    __slots__ = ('vs',)
    def __init__(self, vs):
        self.vs = vs
    def __repr__(self):
        return "Ntms(%s)" % self.vs

class Rec(Val):
    __slots__ = ('x', 'v')
    def __init__(self, x, v):
        self.x = x
        self.v = v
    def __repr__(self):
        return "Rec(\"%s\", %s)" % (self.x, self.v)

def eq_rexp(r1, r2):
    # Structural equality of regular expressions
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
    return False

# Checks if a regular expression matches the empty string
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
    else:
        raise Exception("Unknown regular expression type")

# Derivative of a regular expression with respect to a character
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
    else:
        raise Exception("Unknown regular expression type")

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
    else:
        raise Exception("Unknown regular expression type")

# Derivative of a regular expression with respect to a string
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
    else:
        raise Exception("Unknown regular expression type")

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
    else:
        raise Exception("Unknown value type")

# Environment function to extract the values from a value
def env(v):
    if isinstance(v, Empty):
        return []
    elif isinstance(v, Chr):
        return []
    elif isinstance(v, Left):
        return env(v.v)
    elif isinstance(v, Right):
        return env(v.v)
    elif isinstance(v, Sequ):
        return env(v.v1) + env(v.v2)
    elif isinstance(v, Stars):
        result = []
        for val in v.vs:
            result += env(val)
        return result
    elif isinstance(v, Rng):
        return []
    elif isinstance(v, Pls):
        result = []
        for val in v.vs:
            result += env(val)
        return result
    elif isinstance(v, Opt):
        return env(v.v)
    elif isinstance(v, Ntms):
        result = []
        for val in v.vs:
            result += env(val)
        return result
    elif isinstance(v, Rec):
        return [(v.x, flatten(v.v))] + env(v.v)
    else:
        raise Exception("Unknown value type")

# Make epsilon function to compute HOW a regular expression matches the empty string
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
        return Opt(Empty())
    elif isinstance(r, NTIMES):
        if r.n == 0:
            return Ntms([])
        return Ntms([mkeps(r.r)])
    elif isinstance(r, RECD):
        return Rec(r.x, mkeps(r.r))
    else:
        raise Exception("Unknown regular expression type")

# Injection function to compute HOW a regular expression matches a string
def inj(r, c, v):
    if isinstance(r, STAR):
        sequ = v
        assert isinstance(sequ, Sequ)
        star = sequ.v2
        assert isinstance(star, Stars)
        return Stars([inj(r.r, c, sequ.v1)] + star.vs)
    elif isinstance(r, SEQ):
        if isinstance(v, Sequ):
            return Sequ(inj(r.r1, c, v.v1), v.v2)
        elif isinstance(v, Left):
            seq = v.v
            assert isinstance(seq, Sequ)
            return Sequ(inj(r.r1, c, seq.v1), seq.v2)
        elif isinstance(v, Right):
            return Sequ(mkeps(r.r1), inj(r.r2, c, v.v))
    elif isinstance(r, ALT):
        if isinstance(v, Left):
            return Left(inj(r.r1, c, v.v))
        elif isinstance(v, Right):
            return Right(inj(r.r2, c, v.v))
    elif isinstance(r, CHAR):
        return Chr(c)
    elif isinstance(r, RANGE):
        return Chr(c)
    elif isinstance(r, PLUS):
        if isinstance(v, Sequ):
            star = v.v2
            assert isinstance(star, Stars)
            return Pls([inj(r.r, c, v.v1)] + star.vs)
    elif isinstance(r, OPTIONAL):
        return Opt(inj(r.r, c, v))
    elif isinstance(r, NTIMES):
        if isinstance(v, Sequ):
            assert isinstance(v.v2, Ntms)
            return Ntms([inj(r.r, c, v.v1)] + v.v2.vs)
    elif isinstance(r, RECD):
        return Rec(r.x, inj(r.r, c, v))
    else:
        raise Exception("Unknown regular expression type")

# Rectification tags

TAG_ID          = 0
TAG_RIGHT       = 1
TAG_LEFT        = 2
TAG_ALT         = 3
TAG_SEQ         = 4
TAG_SEQ_EMPTY1  = 5
TAG_SEQ_EMPTY2  = 6
TAG_ERROR       = 7
TAG_RECD        = 8

class RectFun(object):
    __slots__ = ('tag', 'sub1', 'sub2')
    def __init__(self, tag, sub1=None, sub2=None):
        self.tag = tag
        self.sub1 = sub1
        self.sub2 = sub2

def apply_rectfun(rf, v):
    t = rf.tag
    if t == TAG_ID:
        return v
    elif t == TAG_RIGHT:
        return Right(apply_rectfun(rf.sub1, v))
    elif t == TAG_LEFT:
        return Left(apply_rectfun(rf.sub1, v))
    elif t == TAG_ALT:
        if isinstance(v, Left):
            return Left(apply_rectfun(rf.sub1, v.v))
        elif isinstance(v, Right):
            return Right(apply_rectfun(rf.sub2, v.v))
        else:
            raise Exception("Invalid value for TAG_ALT")
    elif t == TAG_SEQ:
        if not isinstance(v, Sequ):
            raise Exception("Invalid value for TAG_SEQ (expected Sequ)")
        v1r = apply_rectfun(rf.sub1, v.v1)
        v2r = apply_rectfun(rf.sub2, v.v2)
        return Sequ(v1r, v2r)
    elif t == TAG_SEQ_EMPTY1:
        empty_part = apply_rectfun(rf.sub1, Empty())
        v2r = apply_rectfun(rf.sub2, v)
        return Sequ(empty_part, v2r)
    elif t == TAG_SEQ_EMPTY2:
        empty_part = apply_rectfun(rf.sub2, Empty())
        v1r = apply_rectfun(rf.sub1, v)
        return Sequ(v1r, empty_part)
    elif t == TAG_ERROR:
        raise Exception("error")
    elif t == TAG_RECD:
        if not isinstance(v, Rec):
            raise Exception("Invalid value for TAG_RECD (expected Rec)")
        v_inner = apply_rectfun(rf.sub1, v.v)
        return Rec(v.x, v_inner)
    else:
        raise Exception("Unknown rectification tag")

# Simplification function

def simp(r):
    if isinstance(r, ALT):
        r1s, f1s = simp(r.r1)
        r2s, f2s = simp(r.r2)
        if isinstance(r1s, ZERO):
            return (r2s, RectFun(TAG_RIGHT, f2s))
        elif isinstance(r2s, ZERO):
            return (r1s, RectFun(TAG_LEFT, f1s))
        elif eq_rexp(r1s, r2s):
            return (r1s, RectFun(TAG_LEFT, f1s))
        else:
            return (ALT(r1s, r2s), RectFun(TAG_ALT, f1s, f2s))
    elif isinstance(r, SEQ):
        r1s, f1s = simp(r.r1)
        r2s, f2s = simp(r.r2)
        if isinstance(r1s, ZERO) or isinstance(r2s, ZERO):
            return (ZERO(), RectFun(TAG_ERROR))
        elif isinstance(r1s, ONE):
            return (r2s, RectFun(TAG_SEQ_EMPTY1, f1s, f2s))
        elif isinstance(r2s, ONE):
            return (r1s, RectFun(TAG_SEQ_EMPTY2, f1s, f2s))
        else:
            return (SEQ(r1s, r2s), RectFun(TAG_SEQ, f1s, f2s))
    else:
        return (r, RectFun(TAG_ID))

# Lexing function
def lex_simp(r, s):
    if not s:
        if nullable(r):
            return mkeps(r)
        else:
            raise Exception("lexing error")
    else:
        c = s[0]
        cs = s[1:]
        r_simp, rf_simp = simp(der(c, r))
        val_sub = lex_simp(r_simp, cs)
        rect_val = apply_rectfun(rf_simp, val_sub)
        return inj(r, c, rect_val)

def lexing_simp(r, s):
    val_result = lex_simp(r, list(s))
    return env(val_result)

# Regular Expressions for the WHILE language

# Keywords
while_regex = SEQ(CHAR("w"), SEQ(CHAR("h"), SEQ(CHAR("i"), SEQ(CHAR("l"), CHAR("e")))))
if_regex = SEQ(CHAR("i"), CHAR("f"))
else_regex = SEQ(CHAR("e"), SEQ(CHAR("l"), SEQ(CHAR("s"), CHAR("e"))))
then_regex = SEQ(CHAR("t"), SEQ(CHAR("h"), SEQ(CHAR("e"), CHAR("n"))))
true_regex = SEQ(CHAR("t"), SEQ(CHAR("r"), SEQ(CHAR("u"), CHAR("e"))))
false_regex = SEQ(CHAR("f"), SEQ(CHAR("a"), SEQ(CHAR("l"), SEQ(CHAR("s"), CHAR("e")))))
read_regex = SEQ(CHAR("r"), SEQ(CHAR("e"), SEQ(CHAR("a"), CHAR("d"))))
write_regex = SEQ(CHAR("w"), SEQ(CHAR("r"), SEQ(CHAR("i"), SEQ(CHAR("t"), CHAR("e")))))

KEYWORD_REGEX = ALT(while_regex, ALT(if_regex, ALT(then_regex, ALT(else_regex, ALT(true_regex, ALT(false_regex, ALT(read_regex, write_regex)))))))

# Operators
plus_regex = CHAR("+")
minus_regex = CHAR("-")
times_regex = CHAR("*")
divide_regex = CHAR("/")
modulus_regex = CHAR("%")
equality_regex = SEQ(CHAR("="), CHAR("="))
not_equal_regex = SEQ(CHAR("!"), CHAR("="))
less_than_regex = CHAR("<")
greater_than_regex = CHAR(">")
less_than_equal_regex = SEQ(CHAR("<"), CHAR("="))
greater_than_equal_regex = SEQ(CHAR(">"), CHAR("="))
assign_regex = SEQ(CHAR(":"), CHAR("="))
and_regex = SEQ(CHAR("&"), CHAR("&"))
or_regex = SEQ(CHAR("|"), CHAR("|"))

OPERATORS_REGEX = ALT(plus_regex, ALT(minus_regex, ALT(times_regex, ALT(divide_regex, ALT(modulus_regex, ALT(equality_regex, ALT(not_equal_regex, ALT(less_than_regex, ALT(greater_than_regex, ALT(less_than_equal_regex, ALT(greater_than_equal_regex, ALT(assign_regex, ALT(and_regex, or_regex)))))))))))))

# Letters and Symbols
LETTERS_REGEX = RANGE("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
full_stop_regex = CHAR(".")
comma_regex = CHAR(",")
semicolon_regex = CHAR(";")
colon_regex = CHAR(":")
underscore_regex = CHAR("_")
equal_regex = CHAR("=")
backslash_regex = CHAR("\\")

SYMBOLS_REGEX = ALT(backslash_regex, ALT(comma_regex, ALT(semicolon_regex, ALT(colon_regex, ALT(underscore_regex, ALT(full_stop_regex, ALT(less_than_regex, ALT(greater_than_regex, ALT(LETTERS_REGEX, equal_regex)))))))))

# Parentheses
left_parenthesis_regex = CHAR("(")
right_parenthesis_regex = CHAR(")")
left_brace_regex = CHAR("{")
right_brace_regex = CHAR("}")

PARENTHESES_REGEX = ALT(left_parenthesis_regex, ALT(right_parenthesis_regex, ALT(left_brace_regex, right_brace_regex)))

# Numbers
DIGITS_REGEX = RANGE("0123456789")
natual_numbers_regex = RANGE("123456789")
NUMBERS_REGEX = ALT(CHAR("0"), SEQ(natual_numbers_regex, STAR(DIGITS_REGEX)))

# Whitespace
WHITESPACE_REGEX = PLUS(RANGE(" \t\n"))

# Identifiers
IDENTIFIER_REGEX = SEQ(LETTERS_REGEX, STAR(ALT(LETTERS_REGEX, ALT(DIGITS_REGEX, underscore_regex))))

# Strings
speech_mark_regex = CHAR("\"")
newline_regex = SEQ(CHAR("\\"), CHAR("n"))
STRING_REGEX = SEQ(speech_mark_regex, SEQ(STAR(ALT(SYMBOLS_REGEX, ALT(DIGITS_REGEX, ALT(PARENTHESES_REGEX, ALT(WHITESPACE_REGEX, newline_regex))))), speech_mark_regex))

# Comments
forward_slashs_regex = SEQ(CHAR("/"), CHAR("/"))
COMMENT_REGEX = SEQ(forward_slashs_regex, SEQ(STAR(ALT(SYMBOLS_REGEX, ALT(CHAR(" "), ALT(PARENTHESES_REGEX, DIGITS_REGEX)))), CHAR("\n")))

# Records for language tokens
KEYWORD_RECORD = RECD("k", KEYWORD_REGEX)
OPERATORS_RECORD = RECD("o", OPERATORS_REGEX)
STRING_RECORD = RECD("str", STRING_REGEX)
PARANTHESES_RECORD = RECD("p", PARENTHESES_REGEX)
SEMICOLON_RECORD = RECD("s", semicolon_regex)
WHITESPACE_RECORD = RECD("w", WHITESPACE_REGEX)
IDENTIFIER_RECORD = RECD("i", IDENTIFIER_REGEX)
NUMBERS_RECORD = RECD("n", NUMBERS_REGEX)
COMMENTS_RECORD = RECD("c", COMMENT_REGEX)

LANGUAGE_REGEX = STAR(ALT(KEYWORD_RECORD, ALT(OPERATORS_RECORD, ALT(STRING_RECORD, ALT(PARANTHESES_RECORD, ALT(SEMICOLON_RECORD, ALT(WHITESPACE_RECORD, ALT(IDENTIFIER_RECORD, ALT(NUMBERS_RECORD, COMMENTS_RECORD)))))))))

# Token classes

class Token:
    __slots__ = ()
    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return self.__class__.__name__

class T_KEYWORD(Token):
    __slots__ = ('s',)
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        return "T_KEYWORD(%s)" % self.s

class T_OP(Token):
    __slots__ = ('s',)
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        return "T_OP(%s)" % self.s

class T_STRING(Token):
    __slots__ = ('s',)
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        return "T_STRING(%s)" % self.s

class T_PAREN(Token):
    __slots__ = ('s',)
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        return "T_PAREN(%s)" % self.s

class T_SEMI(Token):
    __slots__ = ()
    def __init__(self):
        pass
    def __repr__(self):
        return "T_SEMI"

class T_ID(Token):
    __slots__ = ('s',)
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        return "T_ID(%s)" % self.s

class T_NUM(Token):
    __slots__ = ('n',)
    def __init__(self, n):
        self.n = int(n)
    def __repr__(self):
        return "T_NUM(%d)" % self.n

# Tokenise function
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
        return T_SEMI()
    elif kind == "i":
        return T_ID(value)
    elif kind == "n":
        return T_NUM(value)
    else:
        return None

def tokenise(s):
    lexed = lexing_simp(LANGUAGE_REGEX, s)
    result = []
    for pair in lexed:
        tk = token(pair)
        if tk is not None:
            result.append(tk)
    return result

# Main Lexer Function

import os
import time


# For RPython since it does not call the __repr__ method by default
def print_tokens(tokens):
    s = "["
    first = True
    for token in tokens:
        if not first:
            s += ", "
        else:
            first = False
        # Explicitly call the __repr__ method on each token
        s += token.__repr__()
    s += "]"
    return s

def read_file(file):
    cwd = os.getcwd()
    path = os.path.join(os.path.join(cwd, "examples"), file)
    f = open(path, "r")
    content = f.read()
    f.close()
    return content

def lex(filename):
    contents = read_file(filename)
    print("Lex " + filename + ":")
    start = time.time()
    tokens = tokenise(contents)
    print(print_tokens(tokens))
    end = time.time()
    print("Time taken: " + str(end - start) + " seconds")
    return tokens