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

# Test cases for the der function

# Derivative of a sequence of characters
# x1 = der("a", SEQ(CHAR("a"), CHAR("b")))
# print "DER SEQUENCE TEST"
# print(isinstance(x1, SEQ))
# print x1.r1
# print x1.r2.c == "b"  

# Derivative of an alternation of characters
# x2 = der("a", ALT(CHAR("a"), CHAR("b")))
# print "DER ALTERNATION TEST"
# print(isinstance(x2, ALT))
# print x2.r1
# print x2.r2  

# Derivative of a star of a character
# x3 = der("a", STAR(CHAR("a")))
# print "DER STAR TEST"
# print(isinstance(x3, SEQ))
# print x3.r1
# print x3.r2
# print x3.r2.__repr__() ==  "STAR(CHAR(\"a\"))" 
# print RECD("cheese", SEQ(CHAR('c'), SEQ(CHAR('h'), SEQ(CHAR('e'), SEQ(CHAR('e'), SEQ(CHAR("s"), CHAR("e")))))))
# Derivative of a star of a character
# x3 = der("b", STAR(CHAR("a")))
# print "DER STAR FAIL TEST"
# print(isinstance(x3, SEQ))
# print x3.r1
# print x3.r2

# # Derivative of a range of characters
# x4 = der("a", RANGE("abc"))
# print(isinstance(x4, ONE))  # Expected: True

# # Derivative of a plus of a character
# x5 = der("a", PLUS(CHAR("a")))
# print(isinstance(x5, SEQ))  # Expected: True

# # Derivative of an optional character
# x6 = der("a", OPTIONAL(CHAR("a")))
# print(isinstance(x6, ONE))  # Expected: True

# # Derivative of a character not in the range
# x7 = der("d", RANGE("abc"))
# print(isinstance(x7, ZERO))  # Expected: True

# # Derivative of a sequence with nullable first part
# x8 = der("a", SEQ(OPTIONAL(CHAR("a")), CHAR("b")))
# print(isinstance(x8, ALT))  # Expected: True

# # Derivative of a recorded expression
# x9 = der("a", RECD("x", CHAR("a")))
# print(isinstance(x9, ONE))  # Expected: True

# # Derivative of a zero expression
# x10 = der("a", ZERO())
# print(isinstance(x10, ZERO))  # Expected: True

# # Derivative of a one expression
# x11 = der("a", ONE())
# print(isinstance(x11, ZERO))  # Expected: True

# # Derivative of a character that matches
# x12 = der("a", CHAR("a"))
# print(isinstance(x12, ONE))  # Expected: True

# # Derivative of a character that does not match
# x13 = der("b", CHAR("a"))
# print(isinstance(x13, ZERO))  # Expected: True

# # Derivative of a sequence with non-nullable first part
# x14 = der("a", SEQ(CHAR("a"), CHAR("b")))
# print(isinstance(x14, SEQ))  # Expected: True

# # Derivative of a sequence with nullable first part
# x15 = der("a", SEQ(OPTIONAL(CHAR("a")), CHAR("b")))
# print(isinstance(x15, ALT))  # Expected: True

# # Derivative of a star of a sequence
# x16 = der("a", STAR(SEQ(CHAR("a"), CHAR("b"))))
# print(isinstance(x16, SEQ))  # Expected: True

# # Derivative of a plus of a sequence
# x17 = der("a", PLUS(SEQ(CHAR("a"), CHAR("b"))))
# print(isinstance(x17, SEQ))  # Expected: True

# # Derivative of an optional sequence
# x18 = der("a", OPTIONAL(SEQ(CHAR("a"), CHAR("b"))))
# print(isinstance(x18, SEQ))  # Expected: True

# # Derivative of a recorded sequence
# x19 = der("a", RECD("x", SEQ(CHAR("a"), CHAR("b"))))
# print(isinstance(x19, SEQ))  # Expected: True

# # Derivative of a sequence with a range
# x20 = der("a", SEQ(RANGE("abc"), CHAR("b")))
# print(isinstance(x20, SEQ))  # Expected: True



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
    
# print flatten(Sequ(Chr("a"), Chr("b")))  # Expected: "ab"
# print flatten(Stars([Chr("a"), Chr("b"), Chr("c")]))  # Expected: "abc"
# print flatten(Rng([Chr("a"), Chr("b"), Chr("c"), Empty()]))  # Expected: "abc"



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
    
# print env(Rec("x", Chr("a")))  # Expected: [("x", "a")]
# print env(Stars([Rec("x", Chr("a")), Rec("y", Chr("b"))]))  # Expected: [("x", "a"), ("y", "b")]
# print env(Rec("cheese", Sequ(Chr('c'), Sequ(Chr('h'), Sequ(Chr('e'), Sequ(Chr('e'), Sequ(Chr("s"), Chr("e"))))))))

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

# print mkeps(ALT(ONE(), CHAR("a")))  # Expected: Left(Empty)
# x = mkeps(SEQ(ONE(), NTIMES(0, CHAR("D"))))  # Expected: Sequ(Empty, Chr("a"))
# print x.v2

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
    
# regex = SEQ(CHAR("a"), CHAR("b"))
# der1 = der("a", regex)
# print der1
# der2 = der("b", der1)
# print der2
# m = mkeps(der2)
# print m
# i = inj(der1, "b", m)
# print i
# n = inj(regex, "a", i)
# print n
# print flatten(n)

# regex = SEQ(ALT(CHAR("a"), CHAR("b")), CHAR("c"))
# der1 = der("a", regex)
# print der1
# der2 = der("c", der1)
# print der2
# m = mkeps(der2)
# print m
# i = inj(der1, "c", m)
# print i
# n = inj(regex, "a", i)
# print n
# print flatten(n)

# regex = RECD("beans",STAR(CHAR("a")))
# der1 = der("a", regex)
# print der1
# der2 = der("a", der1)
# print der2
# m = mkeps(der2)
# print m
# i = inj(der1, "a", m)
# print i
# n = inj(regex, "a", i)
# print n
# print flatten(n)

regex = NTIMES(CHAR("a"), 3)
der1 = der("a", regex)
print der1
der2 = der("a", der1)
print der2
der3 = der("a", der2)
print der3
m = mkeps(der3)
print m
i = inj(der2, "a", m)
print i
n = inj(der1, "a", i)
print n
a = inj(regex, "a", n)
print a
print flatten(a)

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
        elif r1s == r2s:
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

reg = ALT(ALT(ALT(CHAR("a"), ZERO()), CHAR("c")), CHAR("d"))
print reg
f, g = simp(reg)
print f
print g

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

# print lexing_simp(RECD("CD",STAR(CHAR("a"))), list("aaa"))
print lexing_simp(RECD("AB",NTIMES(CHAR("a"), 3)), list("aaa"))
# print(lexing_simp(SEQ(CHAR("a"), CHAR("b")), "ab"))

# Define regex for keywords in language
while_regex = SEQ(CHAR("w"), SEQ(CHAR("h"), SEQ(CHAR("i"), SEQ(CHAR("l"), CHAR("e")))))
if_regex = SEQ(CHAR("i"), CHAR("f"))
else_regex = SEQ(CHAR("e"), SEQ(CHAR("l"), SEQ(CHAR("s"), CHAR("e"))))
then_regex = SEQ(CHAR("t"), SEQ(CHAR("h"), SEQ(CHAR("e"), CHAR("n"))))
true_regex = SEQ(CHAR("t"), SEQ(CHAR("r"), SEQ(CHAR("u"), CHAR("e"))))
false_regex = SEQ(CHAR("f"), SEQ(CHAR("a"), SEQ(CHAR("l"), SEQ(CHAR("s"), CHAR("e")))))
read_regex = SEQ(CHAR("r"), SEQ(CHAR("e"), SEQ(CHAR("a"), CHAR("d"))))
write_regex = SEQ(CHAR("w"), SEQ(CHAR("r"), SEQ(CHAR("i"), SEQ(CHAR("t"), CHAR("e")))))

print regex_to_string(while_regex)  # Expected: "while"
print regex_to_string(if_regex)  # Expected: "if"
print regex_to_string(else_regex)  # Expected: "else"
print regex_to_string(then_regex)  # Expected: "then"
print regex_to_string(true_regex)  # Expected: "true"
print regex_to_string(false_regex)  # Expected: "false"
print regex_to_string(read_regex)  # Expected: "read"
print regex_to_string(write_regex)  # Expected: "write"


KEYWORD_REGEX = ALT(while_regex, ALT(if_regex, ALT(then_regex, ALT(else_regex, ALT(true_regex, ALT(false_regex, ALT(read_regex, write_regex)))))))


print lexing_simp(RECD("K", KEYWORD_REGEX), list("while"))
print lexing_simp(RECD("K", KEYWORD_REGEX), list("if"))
print lexing_simp(RECD("K", KEYWORD_REGEX), list("then"))
print lexing_simp(RECD("K", KEYWORD_REGEX), list("else"))
print lexing_simp(RECD("K", KEYWORD_REGEX), list("true"))
print lexing_simp(RECD("K", KEYWORD_REGEX), list("false"))
print lexing_simp(RECD("K", KEYWORD_REGEX), list("read"))
print lexing_simp(RECD("K", KEYWORD_REGEX), list("write"))

# Define regex for operations in language
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

print lexing_simp(RECD("O", OPERATORS_REGEX), "+")
print lexing_simp(RECD("O", OPERATORS_REGEX), "-")
print lexing_simp(RECD("O", OPERATORS_REGEX), "*")
print lexing_simp(RECD("O", OPERATORS_REGEX), "/")
print lexing_simp(RECD("O", OPERATORS_REGEX), "%")
print lexing_simp(RECD("O", OPERATORS_REGEX), "==")
print lexing_simp(RECD("O", OPERATORS_REGEX), "!=")
print lexing_simp(RECD("O", OPERATORS_REGEX), "<")
print lexing_simp(RECD("O", OPERATORS_REGEX), ">")
print lexing_simp(RECD("O", OPERATORS_REGEX), "<=")
print lexing_simp(RECD("O", OPERATORS_REGEX), ">=")
print lexing_simp(RECD("O", OPERATORS_REGEX), ":=")
print lexing_simp(RECD("O", OPERATORS_REGEX), "&&")
print lexing_simp(RECD("O", OPERATORS_REGEX), "||")

# Define regex for letters in language
LETTERS_REGEX = RANGE("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")

print lexing_simp(RECD("L", LETTERS_REGEX), "a")
print lexing_simp(RECD("L", LETTERS_REGEX), "Z")

# Define regex for symbols in language
full_stop_regex = CHAR(".")
comma_regex = CHAR(",")
semicolon_regex = CHAR(";")
colon_regex = CHAR(":")
underscore_regex = CHAR("_")
equal_regex = CHAR("=")
backslash_regex = CHAR("\\")

SYMBOLS_REGEX = ALT(backslash_regex, ALT(comma_regex, ALT(semicolon_regex, ALT(colon_regex, ALT(underscore_regex, ALT(full_stop_regex, ALT(less_than_regex, ALT(greater_than_regex, ALT(LETTERS_REGEX, equal_regex)))))))))

print lexing_simp(RECD("S", SYMBOLS_REGEX), ".")
print lexing_simp(RECD("S", SYMBOLS_REGEX), "_")
print lexing_simp(RECD("S", SYMBOLS_REGEX), ">")
print lexing_simp(RECD("S", SYMBOLS_REGEX), "<")
print lexing_simp(RECD("S", SYMBOLS_REGEX), "=")
print lexing_simp(RECD("S", SYMBOLS_REGEX), ";")
print lexing_simp(RECD("S", SYMBOLS_REGEX), ",")
print lexing_simp(RECD("S", SYMBOLS_REGEX), "\\")
print lexing_simp(RECD("S", SYMBOLS_REGEX), ":")
print lexing_simp(RECD("S", SYMBOLS_REGEX), "a")

# Define regex for parentheses in language
left_parenthesis_regex = CHAR("(")
right_parenthesis_regex = CHAR(")")
left_brace_regex = CHAR("{")
right_brace_regex = CHAR("}")

PARENTHESES_REGEX = ALT(left_parenthesis_regex, ALT(right_parenthesis_regex, ALT(left_brace_regex, right_brace_regex)))

print lexing_simp(RECD("P", PARENTHESES_REGEX), "(")
print lexing_simp(RECD("P", PARENTHESES_REGEX), ")")
print lexing_simp(RECD("P", PARENTHESES_REGEX), "{")
print lexing_simp(RECD("P", PARENTHESES_REGEX), "}")

# Define regex for numbers in language
DIGITS_REGEX = RANGE("0123456789")

print lexing_simp(RECD("D", DIGITS_REGEX), "0")
print lexing_simp(RECD("D", DIGITS_REGEX), "9")

# Define regex for whitespace in language
WHITESPACE_REGEX = PLUS(RANGE(" \t\n"))

print lexing_simp(RECD("W", WHITESPACE_REGEX), "     ")
print lexing_simp(RECD("W", WHITESPACE_REGEX), "\t")
print lexing_simp(RECD("W", WHITESPACE_REGEX), "\n")

# Define regex for identifiers in language
IDENTIFIER_REGEX = SEQ(LETTERS_REGEX, STAR(ALT(LETTERS_REGEX, ALT(DIGITS_REGEX, underscore_regex))))

print lexing_simp(RECD("I", IDENTIFIER_REGEX), "ab_s_")
print lexing_simp(RECD("I", IDENTIFIER_REGEX), "Zdw90_")

# Define regex for numbers in language
natual_numbers_regex = RANGE("123456789")

NUMBERS_REGEX = ALT(CHAR("0"), SEQ(natual_numbers_regex, STAR(DIGITS_REGEX)))

print lexing_simp(RECD("N", NUMBERS_REGEX), "0")
print lexing_simp(RECD("N", NUMBERS_REGEX), "1")
print lexing_simp(RECD("N", NUMBERS_REGEX), "903")

# Define regex for strings in language
speech_mark_regex = CHAR("\"")
newline_regex = SEQ(CHAR("\\"), CHAR("n"))

STRING_REGEX = SEQ(speech_mark_regex, SEQ(STAR(ALT(SYMBOLS_REGEX, ALT(DIGITS_REGEX, ALT(PARENTHESES_REGEX, ALT(WHITESPACE_REGEX, newline_regex))))), speech_mark_regex))

print lexing_simp(RECD("S", STRING_REGEX), "\"a\"")
print lexing_simp(RECD("S", STRING_REGEX), "\"Hello World\\n\"")

# Define regex for commennts in language
forward_slashs_regex = SEQ(CHAR("/"), CHAR("/"))

COMMENT_REGEX = SEQ(forward_slashs_regex, STAR(ALT(SYMBOLS_REGEX, ALT(DIGITS_REGEX, ALT(PARENTHESES_REGEX, ALT(WHITESPACE_REGEX, newline_regex))))))

print lexing_simp(RECD("C", COMMENT_REGEX), "// a my e re ")

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

s = """
while a == 0 {
    a := a + 1
};
"""
print lexing_simp(LANGUAGE_REGEX, s)
# print lexing_simp(LANGUAGE_REGEX, "while a == 0")

# Tokens
class Token:

    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return self.__class__.__name__

class T_KEYWORD(Token):
    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "T_KEYWORD(\"%s\")" % self.s

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

print tokenise(s)