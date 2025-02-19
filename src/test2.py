from rpython.rlib import set as rset
from rpython.rlib.objectmodel import instantiate
from rpython.rtyper.extregistry import ExtRegistryEntry

# Regular expressions
class Rexp:
    pass

class ZERO(Rexp):
    pass

class ONE(Rexp):
    pass

class CHAR(Rexp):
    def __init__(self, c):
        self.c = c

class ALT(Rexp):
    def __init__(self, r1, r2):
        self.r1 = r1
        self.r2 = r2

class SEQ(Rexp):
    def __init__(self, r1, r2):
        self.r1 = r1
        self.r2 = r2

class STAR(Rexp):
    def __init__(self, r):
        self.r = r

# New regular expressions
class RANGE(Rexp):
    def __init__(self, s):
        self.s = s  # Expecting a rset (set of characters)

class PLUS(Rexp):
    def __init__(self, r):
        self.r = r

class OPTIONAL(Rexp):
    def __init__(self, r):
        self.r = r

class NTIMES(Rexp):
    def __init__(self, r, n):
        self.r = r
        self.n = n

class RECD(Rexp):
    def __init__(self, x, r):
        self.x = x
        self.r = r

# Values
class Val:
    pass

class Empty(Val):
    pass

class Chr(Val):
    def __init__(self, c):
        self.c = c

class Sequ(Val):
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

class Left(Val):
    def __init__(self, v):
        self.v = v

class Right(Val):
    def __init__(self, v):
        self.v = v

class Stars(Val):
    def __init__(self, vs):
        self.vs = vs  # List of Val

# New values for new regular expressions
class Rng(Val):
    def __init__(self, cs):
        self.cs = cs  # rset of Val

class Pls(Val):
    def __init__(self, vs):
        self.vs = vs  # List of Val

class Opt(Val):
    def __init__(self, v):
        self.v = v

class Ntms(Val):
    def __init__(self, vs):
        self.vs = vs  # List of Val

class Rec(Val):
    def __init__(self, x, v):
        self.x = x
        self.v = v

def charlist2rexp(s):
    """Convert a list of characters to a regular expression."""
    if not s:
        return ONE()
    elif len(s) == 1:
        return CHAR(s[0])
    else:
        return SEQ(CHAR(s[0]), charlist2rexp(s[1:]))

def string_to_rexp(s):
    """Convert a string to a regular expression."""
    return charlist2rexp(list(s))

# Nullable function to check if a regular expression can derive the empty string
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
        return r.n == 0 or nullable(r.r)
    elif isinstance(r, RECD):
        return nullable(r.r)

# Convenience extensions for string to Rexp conversion
class StringExtensions:
    def __init__(self, s):
        self.s = s

    def __and__(self, r):
        return RECD(self.s, r)

    def __or__(self, r):
        return ALT(string_to_rexp(self.s), r)

    def __mod__(self):
        return STAR(string_to_rexp(self.s))

    def __tilde__(self, r):
        return SEQ(string_to_rexp(self.s), r)

# Extend string with the convenience methods
def extend_string_methods():
    import rpython.rtyper.extregistry as extregistry
    extregistry.add_class_extension(StringExtensions)

# Derivative function for regular expressions
def der(c, r):
    if isinstance(r, ZERO):
        return ZERO()
    elif isinstance(r, ONE):
        return ZERO()
    elif isinstance(r, CHAR):
        return ONE() if c == r.c else ZERO()
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
        return ONE() if c in r.s else ZERO()
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

# Example usages
# Note: Actual testing or usage would be added later in the lexer or in unit tests.

# Flatten function for values
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
        return ''.join(flatten(vs) for vs in v.vs)
    elif isinstance(v, Rng):
        return ''.join(flatten(cs) for cs in v.cs)
    elif isinstance(v, Pls):
        return ''.join(flatten(vs) for vs in v.vs)
    elif isinstance(v, Opt):
        return flatten(v.v)
    elif isinstance(v, Ntms):
        return ''.join(flatten(vs) for vs in v.vs)
    elif isinstance(v, Rec):
        return flatten(v.v)

# Example usages
# Note: Actual testing or usage would be added later in the lexer or in unit tests.

# Environment extraction function
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
        return [pair for vs in v.vs for pair in env(vs)]
    elif isinstance(v, Rng):
        return []
    elif isinstance(v, Pls):
        return [pair for vs in v.vs for pair in env(vs)]
    elif isinstance(v, Opt):
        return env(v.v)
    elif isinstance(v, Ntms):
        return [pair for vs in v.vs for pair in env(vs)]
    elif isinstance(v, Rec):
        return [(v.x, flatten(v.v))] + env(v.v)

# Example usages
# Note: Actual testing or usage would be added later in the lexer or in unit tests.

# Epsilon generation function
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
        return Stars([])  # Represents epsilon for STAR
    elif isinstance(r, PLUS):
        return Pls([mkeps(r.r)])  # Represents epsilon for PLUS
    elif isinstance(r, OPTIONAL):
        return Opt(Empty())  # Represents epsilon for OPTIONAL
    elif isinstance(r, NTIMES):
        if r.n == 0:
            return Ntms([])  # Represents epsilon for NTIMES with 0 repetitions
        else:
            return Ntms([mkeps(r.r)])  # Generates the epsilon value for n > 0
    elif isinstance(r, RECD):
        return Rec(r.x, mkeps(r.r))  # For recursive definitions
    else:
        raise ValueError("Unsupported Rexp type")

# Inject function
def inj(r, c, v):
    if isinstance(r, STAR):
        if isinstance(v, Sequ):
            return Stars([inj(r.r, c, v.v1)] + v.vs)
        else:
            raise ValueError("Expected Sequ for STAR")
    
    elif isinstance(r, SEQ):
        if isinstance(v, Sequ):
            return Sequ(inj(r.r1, c, v.v1), v.v2)
        elif isinstance(v, Left):
            return Sequ(inj(r.r1, c, v.v), v.v2)
        elif isinstance(v, Right):
            return Sequ(mkeps(r.r1), inj(r.r2, c, v.v))
        else:
            raise ValueError("Expected Sequ, Left, or Right for SEQ")

    elif isinstance(r, ALT):
        if isinstance(v, Left):
            return Left(inj(r.r1, c, v.v))
        elif isinstance(v, Right):
            return Right(inj(r.r2, c, v.v))
        else:
            raise ValueError("Expected Left or Right for ALT")

    elif isinstance(r, CHAR):
        if isinstance(v, Empty):
            return Chr(c)
        else:
            raise ValueError("Expected Empty for CHAR")

    # New regular expressions
    elif isinstance(r, RANGE):
        if isinstance(v, Empty):
            return Chr(c)
        else:
            raise ValueError("Expected Empty for RANGE")

    elif isinstance(r, PLUS):
        if isinstance(v, Sequ):
            return Pls([inj(r.r, c, v.v1)] + v.vs)
        else:
            raise ValueError("Expected Sequ for PLUS")

    elif isinstance(r, OPTIONAL):
        return Opt(inj(r.r, c, v))

    elif isinstance(r, NTIMES):
        if isinstance(v, Sequ):
            return Ntms([inj(r.r, c, v.v1)] + v.vs)
        else:
            raise ValueError("Expected Sequ for NTIMES")

    elif isinstance(r, RECD):
        return Rec(r.x, inj(r.r, c, v))

    else:
        raise ValueError("Unsupported Rexp type")

def F_ID(v):
    return v

def F_RIGHT(f):
    def wrapper(v):
        return Right(f(v))
    return wrapper

def F_LEFT(f):
    def wrapper(v):
        return Left(f(v))
    return wrapper

def F_ALT(f1, f2):
    def wrapper(v):
        if isinstance(v, Right):
            return Right(f2(v))
        elif isinstance(v, Left):
            return Left(f1(v))
    return wrapper

def F_SEQ(f1, f2):
    def wrapper(v):
        if isinstance(v, Sequ):
            return Sequ(f1(v.v1), f2(v.v2))
    return wrapper

def F_SEQ_Empty1(f1, f2):
    def wrapper(v):
        return Sequ(f1(Empty), f2(v))
    return wrapper

def F_SEQ_Empty2(f1, f2):
    def wrapper(v):
        return Sequ(f1(v), f2(Empty))
    return wrapper

def F_RECD(f):
    def wrapper(v):
        if isinstance(v, Rec):
            return Rec(v.x, f(v.v))
    return wrapper

def F_ERROR(v):
    raise Exception("error")
