# CW 2
#======

# Rexps
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

# new regular expressions
class RANGE(Rexp):
    def __init__(self, s):
        self.s = s

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

# Values - you might have to extend them 
# according to which values you want to create
# for the new regular expressions
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
        self.vs = vs

class Rec(Val):
    def __init__(self, x, v):
        self.x = x
        self.v = v

# new values for new regular expressions
class Rng(Val):
    def __init__(self, cs):
        self.cs = cs

class Pls(Val):
    def __init__(self, vs):
        self.vs = vs

class Opt(Val):
    def __init__(self, v):
        self.v = v

class Ntms(Val):
    def __init__(self, vs):
        self.vs = vs

# TODO NEED TO ADD IMPLICIT CONVERSIONS

# Nullable function (needs to be extended for new regular expressions)

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
    # new regular expressions
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
    else:
        raise TypeError("Unknown Rexp type")
    
# Derivative function (needs to be extended for new regular expressions)

def der(c, r):
    if isinstance(r, ZERO):
        return ZERO()
    elif isinstance(r, ONE):
        return ZERO()
    elif isinstance(r, CHAR):
        return ONE() if r.c == c else ZERO()
    elif isinstance(r, ALT):
        return ALT(der(c, r.r1), der(c, r.r2))
    elif isinstance(r, SEQ):
        if nullable(r.r1):
            return ALT(SEQ(der(c, r.r1), r.r2), der(c, r.r2))
        else:
            return SEQ(der(c, r.r1), r.r2)
    elif isinstance(r, STAR):
        return SEQ(der(c, r.r), STAR(r.r))
    # new regular expressions
    elif isinstance(r, RANGE):
        return ONE() if c in r.s else ZERO()
    elif isinstance(r, PLUS):
        return SEQ(der(c, r.r), STAR(r.r))
    elif isinstance(r, OPTIONAL):
        return der(c, r.r)
    elif isinstance(r, NTIMES):
        return ZERO() if r.n == 0 else SEQ(der(c, r.r), NTIMES(r.r, r.n - 1))
    elif isinstance(r, RECD):
        return der(c, r.r)
    else:
        raise TypeError("Unknown Rexp type")
    
# Flatten function (needs to work with all values)

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
        return "".join([flatten(vs) for vs in v.vs])
    # new values
    elif isinstance(v, Rng):
        return "".join([flatten(Chr(c)) for c in v.cs])
    elif isinstance(v, Pls):
        return "".join([flatten(vs) for vs in v.vs])
    elif isinstance(v, Opt):
        return flatten(v.v)
    elif isinstance(v, Ntms):
        return "".join([flatten(vs) for vs in v.vs])
    elif isinstance(v, Rec):
        return flatten(v.v)
    else:
        raise TypeError("Unknown Val type")
    
# Environment function (needs to work with all values)

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
        for vs in v.vs:
            result.extend(env(vs))
        return result
    # new values
    elif isinstance(v, Rng):
        return []
    elif isinstance(v, Pls):
        result = []
        for vs in v.vs:
            result.extend(env(vs))
        return result
    elif isinstance(v, Opt):
        return env(v.v)
    elif isinstance(v, Ntms):
        result = []
        for vs in v.vs:
            result.extend(env(vs))
        return result
    elif isinstance(v, Rec):
        return [(v.x, flatten(v.v))] + env(v.v)
    else:
        raise TypeError("Unknown Val type")
    
# mkeps function (needs to be extended for new regular expressions)

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
    # new regular expressions
    elif isinstance(r, PLUS):
        return Pls([mkeps(r.r)])
    elif isinstance(r, OPTIONAL):
        return Opt(Empty())
    elif isinstance(r, NTIMES):
        if r.n == 0:
            return Ntms([])
        else:
            return Ntms([mkeps(r.r)])
    elif isinstance(r, RECD):
        return Rec(r.x, mkeps(r.r))
    else:
        raise TypeError("Unknown Rexp type")