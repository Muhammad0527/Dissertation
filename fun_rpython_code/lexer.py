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

# The Lexing Rules for the FUN Language

# Define regex for symbols in language
SYM_REGEX = RANGE("abcdefghijklmnopqrstuvwxyzT_")

# Define regex for uppercase symbols in language
UPPERCASE_REGEX = RANGE("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# Define digits
DIGIT_REGEX = RANGE("0123456789")

# Define constants
CONST_REGEX = SEQ(UPPERCASE_REGEX, STAR(ALT(SYM_REGEX, DIGIT_REGEX)))

# Define regex for IDs
ID_REGEX = SEQ(SYM_REGEX, STAR(ALT(SYM_REGEX, DIGIT_REGEX)))

# Define regex for integers
INT_REGEX = ALT(SEQ(OPTIONAL(CHAR("-")), CHAR("0")), SEQ(OPTIONAL(CHAR("-")), SEQ(RANGE("123456789"), STAR(DIGIT_REGEX))))

# Define regex for doubles
DOUBLE_REGEX = SEQ(SEQ(OPTIONAL(CHAR("-")), ALT(CHAR("0"), INT_REGEX)), SEQ(CHAR("."), PLUS(DIGIT_REGEX)))

# Define regex for keywords
IF_REGEX = SEQ(CHAR("i"), CHAR("f"))
THEN_REGEX = SEQ(CHAR("t"), SEQ(CHAR("h"), SEQ(CHAR("e"), CHAR("n"))))
ELSE_REGEX = SEQ(CHAR("e"), SEQ(CHAR("l"), SEQ(CHAR("s"), CHAR("e"))))
DEF_REGEX = SEQ(CHAR("d"), SEQ(CHAR("e"), CHAR("f")))
VAL_REGEX = SEQ(CHAR("v"), SEQ(CHAR("a"), CHAR("l")))

KEYWORDS_REGEX = ALT(ALT(ALT(ALT(IF_REGEX, THEN_REGEX), ELSE_REGEX), DEF_REGEX), VAL_REGEX)

# Define regex for types
INT_TYPE_REGEX = SEQ(CHAR("I"), SEQ(CHAR("n"), CHAR("t")))
DOUBLE_TYPE_REGEX = SEQ(CHAR("D"), SEQ(CHAR("o"), SEQ(CHAR("u"), SEQ(CHAR("b"), SEQ(CHAR("l"), CHAR("e"))))))
VOID_TYPE_REGEX = SEQ(CHAR("V"), SEQ(CHAR("o"), SEQ(CHAR("i"), CHAR("d"))))

TYPE_REGEX = ALT(ALT(INT_TYPE_REGEX, DOUBLE_TYPE_REGEX), VOID_TYPE_REGEX)

# Define regex for semicolon
SEMICOLON_REGEX = CHAR(";")

# Define regex for colon
COLON_REGEX = CHAR(":")

# Define regex for operators
PLUS_REGEX = CHAR("+")
MINUS_REGEX = CHAR("-")
TIMES_REGEX = CHAR("*")
DIVIDE_REGEX = CHAR("/")
MODULO_REGEX = CHAR("%")
DEFINE_REGEX = CHAR("=")
EQALITY_REGEX = SEQ(CHAR("="), CHAR("="))
INEQUALITY_REGEX = SEQ(CHAR("!"), CHAR("="))
LESS_THAN_REGEX = CHAR("<")
GREATER_THAN_REGEX = CHAR(">")
LESS_THAN_EQ_REGEX = SEQ(CHAR("<"), CHAR("="))
GREATER_THAN_EQ_REGEX = SEQ(CHAR(">"), CHAR("="))

OPERATORS_REGEX = ALT(PLUS_REGEX, ALT(MINUS_REGEX, ALT(TIMES_REGEX, ALT(DIVIDE_REGEX, ALT(MODULO_REGEX, ALT(DEFINE_REGEX, ALT(EQALITY_REGEX, ALT(INEQUALITY_REGEX, ALT(LESS_THAN_REGEX, ALT(GREATER_THAN_REGEX, ALT(LESS_THAN_EQ_REGEX, GREATER_THAN_EQ_REGEX)))))))))))

# Define regex for whitespace
WHITESPACE_REGEX = RANGE(" \n\t\r")

# Define regex for parentheses
LEFT_PAREN_REGEX = CHAR("(")
RIGHT_PAREN_REGEX = CHAR(")")
LEFT_BRACE_REGEX = CHAR("{")
RIGHT_BRACE_REGEX = CHAR("}")

# Define regex for commas
COMMA_REGEX = CHAR(",")

# Define regex for "all"
SPEECH_MARK_REGEX = CHAR("\"")
ALL_REGEX = ALT(SYM_REGEX, ALT(DIGIT_REGEX, ALT(UPPERCASE_REGEX, ALT(OPERATORS_REGEX, ALT(INT_REGEX, ALT(DOUBLE_REGEX, ALT(CHAR(" "), ALT(COLON_REGEX, ALT(SEMICOLON_REGEX, ALT(SPEECH_MARK_REGEX, ALT(DEFINE_REGEX, ALT(COMMA_REGEX, ALT(LEFT_PAREN_REGEX, ALT(RIGHT_PAREN_REGEX, ALT(LEFT_BRACE_REGEX, RIGHT_BRACE_REGEX)))))))))))))))

# Define regex for strings
NEW_LINE_REGEX = SEQ(CHAR("\\"), CHAR("n"))
STRING_REGEX = SEQ(SPEECH_MARK_REGEX, SEQ(STAR(ALT(ALL_REGEX, NEW_LINE_REGEX)), SPEECH_MARK_REGEX))

# Define regex for char literals
QUOTE_REGEX = CHAR("'")
CHAR_LITERAL_REGEX = SEQ(QUOTE_REGEX, SEQ(ALT(SYM_REGEX, ALT(UPPERCASE_REGEX, ALT(DIGIT_REGEX, ALT(OPERATORS_REGEX, ALT(WHITESPACE_REGEX, ALT(COMMA_REGEX, NEW_LINE_REGEX)))))), QUOTE_REGEX))

# Define regex for comments
ALL2_REGEX = ALT(ALL_REGEX, CHAR("\n"))
OPEN_COMMENT_REGEX = SEQ(CHAR("/"), CHAR("*"))
CLOSE_COMMENT_REGEX = SEQ(CHAR("*"), CHAR("/"))
DOUBLE_SLASH_REGEX = SEQ(CHAR("/"), CHAR("/"))
COMMENT_REGEX = ALT(SEQ(OPEN_COMMENT_REGEX, SEQ(STAR(ALL2_REGEX), CLOSE_COMMENT_REGEX)), SEQ(DOUBLE_SLASH_REGEX, SEQ(STAR(ALL_REGEX), CHAR("\n"))))

# Define records for the FUN language
KEWORD_RECORD = RECD("k", KEYWORDS_REGEX)
ID_RECORD = RECD("i", ID_REGEX)
TYPE_RECORD = RECD("t", TYPE_REGEX)
CONST_RECORD = RECD("ct", CONST_REGEX)
STRING_RECORD = RECD("str", STRING_REGEX)
OPERATOR_RECORD = RECD("o", OPERATORS_REGEX)
INT_RECORD = RECD("int", INT_REGEX)
DOUBLE_RECORD = RECD("d", DOUBLE_REGEX)
SEMICOLON_RECORD = RECD("s", SEMICOLON_REGEX)
COLON_RECORD = RECD("cl", COLON_REGEX)
CHAR_LITERAL_RECORD = RECD("cr", CHAR_LITERAL_REGEX)
COMMA_RECORD = RECD("c", COMMA_REGEX)
LEFT_PAREN_RECORD = RECD("pl", LEFT_PAREN_REGEX)
RIGHT_PAREN_RECORD = RECD("pr", RIGHT_PAREN_REGEX)
LEFT_BRACE_RECORD = RECD("bl", LEFT_BRACE_REGEX)
RIGHT_BRACE_RECORD = RECD("br", RIGHT_BRACE_REGEX)
COMMENTS_RECORD = RECD("w", ALT(COMMENT_REGEX, WHITESPACE_REGEX))

# Define regex for the FUN language
FUN_REGEX = STAR(ALT(KEWORD_RECORD, ALT(ID_RECORD, ALT(TYPE_RECORD, ALT(CONST_RECORD, ALT(STRING_RECORD, ALT(OPERATOR_RECORD, ALT(INT_RECORD, ALT(DOUBLE_RECORD, ALT(SEMICOLON_RECORD, ALT(COLON_RECORD, ALT(CHAR_LITERAL_RECORD, ALT(COMMA_RECORD, ALT(LEFT_PAREN_RECORD, ALT(RIGHT_PAREN_RECORD, ALT(LEFT_BRACE_RECORD, ALT(RIGHT_BRACE_RECORD, COMMENTS_RECORD)))))))))))))))))

# Tokens for the fun language

# Base token class
class Token:
    __slots__ = ()
    def __repr__(self):
        return self.__class__.__name__

# Tokens without payloads
class T_SEMI(Token): 
    __slots__ = ()

class T_COLON(Token): 
    __slots__ = ()

class T_COMMA(Token): 
    __slots__ = ()

class T_LPAREN(Token): 
    __slots__ = ()

class T_RPAREN(Token): 
    __slots__ = ()

class T_LBRACE(Token): 
    __slots__ = ()

class T_RBRACE(Token): 
    __slots__ = ()

# Tokens with payloads
class T_ID(Token):
    __slots__ = ('s',)

    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "T_ID(%s)" % self.s

class T_TYPE(Token):
    __slots__ = ('s',)

    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "T_TYPE(%s)" % self.s

class T_CONST(Token):
    __slots__ = ('s',)

    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "T_CONST(%s)" % self.s

class T_CHAR(Token):
    __slots__ = ('c',)

    def __init__(self, c):
        self.c = c

    def __repr__(self):
        return "T_CHAR(%d)" % self.c

class T_STRING(Token):
    __slots__ = ('s',)

    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "T_STRING(%s)" % self.s

class T_OP(Token):
    __slots__ = ('s',)

    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "T_OP(%s)" % self.s

class T_INT(Token):
    __slots__ = ('n',)

    def __init__(self, n):
        self.n = n

    def __repr__(self):
        return "T_INT(%d)" % self.n

class T_DOUBLE(Token):
    __slots__ = ('n',)

    def __init__(self, n):
        self.n = n

    def __repr__(self):
        return "T_DOUBLE(%s)" % self.n

class T_KWD(Token):
    __slots__ = ('s',)
    
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        return "T_KWD(%s)" % self.s

# ----------------------------------------------------------------------------
# MAPPING (tag, string) --> Token
# ----------------------------------------------------------------------------

def token(pair):
    kind, value = pair
    if kind == "k":      # keyword
        return T_KWD(value)
    elif kind == "i":    # identifier
        return T_ID(value)
    elif kind == "t":    # type
        return T_TYPE(value)
    elif kind == "ct":   # constant
        return T_CONST(value)
    elif kind == "cr":   # character literal
        # Special-case: if the literal is "'\\n'", then return newline
        if value == "'\\n'":
            return T_CHAR(10)
        else:
            # Assumes token is of the form "'x'"
            return T_CHAR(ord(value[1]))
    elif kind == "o":    # operator
        return T_OP(value)
    elif kind == "str":  # string literal
        return T_STRING(value)
    elif kind == "int":  # integer
        return T_INT(int(value))
    elif kind == "d":    # double
        return T_DOUBLE(float(value))
    elif kind == "s":    # semicolon
        return T_SEMI()
    elif kind == "cl":   # colon
        return T_COLON()
    elif kind == "c":    # comma
        return T_COMMA()
    elif kind == "pl":   # left parenthesis
        return T_LPAREN()
    elif kind == "pr":   # right parenthesis
        return T_RPAREN()
    elif kind == "bl":   # left brace
        return T_LBRACE()
    elif kind == "br":   # right brace
        return T_RBRACE()
    else:
        return None

def tokenise(s):
    lexed = lexing_simp(FUN_REGEX, s)
    result = []
    for pair in lexed:
        tk = token(pair)
        if tk is not None:
            result.append(tk)
    return result

# Main Lexer Function

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

def lex(contents):
    print("Lex:")
    start = time.time()
    tokens = tokenise(contents)
    end = time.time()
    print(print_tokens(tokens))
    print("Lexing Time taken: " + str(end - start) + " seconds")
    return tokens