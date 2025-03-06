from lexer import T_ID, T_OP, T_NUM, T_SEMI, T_KEYWORD, T_STRING, T_PAREN

# AST classes

class Stmt(object):
    pass

class Skip(Stmt):
    
    def __repr__(self):
        return "Skip()"

class If(Stmt):
    __slots__ = ('bexp', 'block_then', 'block_else')

    def __init__(self, bexp, block_then, block_else):
        self.bexp = bexp
        self.block_then = block_then
        self.block_else = block_else

    def __repr__(self):
        return "If(%r, %r, %r)" % (self.bexp, self.block_then, self.block_else)

class While(Stmt):
    __slots__ = ('bexp', 'block')

    def __init__(self, bexp, block):
        self.bexp = bexp
        self.block = block

    def __repr__(self):
        return "While(%r, %r)" % (self.bexp, self.block)
    

class Assign(Stmt):
    __slots__ = ('varname', 'aexp')

    def __init__(self, varname, aexp):
        self.varname = varname
        self.aexp = aexp

    def __repr__(self):
        return "Assign(%r, %r)" % (self.varname, self.aexp)

class Read(Stmt):
    __slots__ = ('varname',)

    def __init__(self, varname):
        self.varname = varname

    def __repr__(self):
        return "Read(%r)" % self.varname

class WriteId(Stmt):
    __slots__ = ('varname',)

    def __init__(self, varname):
        self.varname = varname

    def __repr__(self):
        return "WriteId(%r)" % self.varname

class WriteString(Stmt):
    __slots__ = ('text',)

    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return "WriteString(%r)" % self.text

class AExp(object):
    pass

class Var(AExp):
    __slots__ = ('s',)

    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return "Var(%r)" % self.s

class Num(AExp):
    __slots__ = ('i',)

    def __init__(self, i):
        self.i = i

    def __repr__(self):
        return "Num(%r)" % self.i

class Aop(AExp):
    __slots__ = ('op', 'left', 'right')

    def __init__(self, op, left, right):
        self.op = op 
        self.left = left
        self.right = right

    def __repr__(self):
        return "Aop(%r, %r, %r)" % (self.op, self.left, self.right)

class BExp(object):
    pass

class TrueConst(BExp):

    def __repr__(self):
        return "TrueConst()"

class FalseConst(BExp):

    def __repr__(self):
        return "FalseConst()"

class Bop(BExp):
    __slots__ = ('op', 'left', 'right')

    def __init__(self, op, left, right):
        self.op = op  
        self.left = left   
        self.right = right

    def __repr__(self):
        return "Bop(%r, %r, %r)" % (self.op, self.left, self.right)

class Lop(BExp):
    __slots__ = ('op', 'left', 'right')

    def __init__(self, op, left, right):
        self.op = op  
        self.left = left
        self.right = right

    def __repr__(self):
        return "Lop(%r, %r, %r)" % (self.op, self.left, self.right)

# Helper functions for parsing

class ParseError(Exception):
    pass

def peek_token(tokens, i):
    """Return tokens[i] if in range, otherwise None."""
    if i < len(tokens):
        return tokens[i]
    return None

def match_keyword(tokens, i, kw):
    """
    If tokens[i] is a T_KEYWORD(kw), return (True, i+1).
    Otherwise return (False, i).
    """
    t = peek_token(tokens, i)
    if t is not None and isinstance(t, T_KEYWORD) and t.s == kw:
        return True, i + 1
    return False, i

def match_op(tokens, i, op):
    """
    If tokens[i] is T_OP(op), return (True, i+1).
    Otherwise return (False, i).
    """
    t = peek_token(tokens, i)
    if t is not None and isinstance(t, T_OP) and t.s == op:
        return True, i + 1
    return False, i

def match_paren(tokens, i, par):
    """
    If tokens[i] is T_PAREN(par), return (True, i+1).
    Otherwise return (False, i).
    """
    t = peek_token(tokens, i)
    if t is not None and isinstance(t, T_PAREN) and t.s == par:
        return True, i + 1
    return False, i

def match_semi(tokens, i):
    """
    If tokens[i] is T_SEMI, return (True, i+1).
    Otherwise return (False, i).
    """
    t = peek_token(tokens, i)
    if isinstance(t, T_SEMI):
        return True, i + 1
    return False, i

def match_id(tokens, i):
    """
    If tokens[i] is T_ID(...), return (string_of_id, i+1).
    Otherwise raise ParseError.
    """
    t = peek_token(tokens, i)
    if t is not None and isinstance(t, T_ID):
        return t.s, i + 1
    raise ParseError("Expected identifier at position %d" % i)

def match_num(tokens, i):
    """
    If tokens[i] is T_NUM(...), return (int_value, i+1).
    Otherwise raise ParseError.
    """
    t = peek_token(tokens, i)
    if t is not None and isinstance(t, T_NUM):
        return t.n, i + 1
    raise ParseError("Expected number at position %d" % i)

def match_string(tokens, i):
    """
    If tokens[i] is T_STRING(...), return (string_value, i+1).
    Otherwise raise ParseError.
    """
    t = peek_token(tokens, i)
    if t is not None and isinstance(t, T_STRING):
        return t.s, i + 1
    raise ParseError("Expected string literal at position %d" % i)



# Arithmetic expressions

def parse_aexp(tokens, i):
    """
    AExp -> Te ( ('+'|'-') AExp ) || Te
    """
    left, i = parse_te(tokens, i)
    while True:
        t = peek_token(tokens, i)
        if t is None:
            break
        if isinstance(t, T_OP) and (t.s == "+" or t.s == "-"):
            op = t.s
            i += 1
            # parse the "right" as aexp again
            right, i = parse_te(tokens, i)
            left = Aop(op, left, right)
        else:
            break
    return left, i

def parse_te(tokens, i):
    """
    Te -> Fa ( ('*'|'/'|'%') Te ) || Fa
    """
    left, i = parse_fa(tokens, i)
    while True:
        t = peek_token(tokens, i)
        if t is None:
            break
        if isinstance(t, T_OP) and (t.s == "*" or t.s == "/" or t.s == "%"):
            op = t.s
            i += 1
            right, i = parse_fa(tokens, i)
            left = Aop(op, left, right)
        else:
            break
    return left, i

def parse_fa(tokens, i):
    matched, i2 = match_paren(tokens, i, "(")
    if matched:
        # parse AExp
        node, i2 = parse_aexp(tokens, i2)
        # expect ')'
        matched2, i2 = match_paren(tokens, i2, ")")
        if not matched2:
            raise ParseError("Missing ')' after '(' AExp at position %d" % i2)
        return node, i2

    # else if T_ID
    t = peek_token(tokens, i)
    if isinstance(t, T_ID):
        varname, i2 = match_id(tokens, i)
        return Var(varname), i2

    # else if T_NUM
    if isinstance(t, T_NUM):
        numval, i2 = match_num(tokens, i)
        return Num(numval), i2

    raise ParseError("Expected '(' AExp ')' or ID or number at position %d" % i)


# Boolean expressions

def parse_bexp(tokens, i):
    """
      BExp -> 
        AExp '==' AExp
      | AExp '!=' AExp
      | AExp '<'  AExp
      | AExp '>'  AExp
      | AExp '<=' AExp
      | AExp '>=' AExp
      | '(' BExp ')' '&&' BExp
      | '(' BExp ')' '||' BExp
      | '(' BExp ')' 
      | 'true'
      | 'false'
    """
    orig_i = i
    # try relational expressions: AExp op AExp
    try:
        left, i2 = parse_aexp(tokens, i)
    except Exception:
        # if AExp fails, we can try other alternatives below.
        i2 = i
        left = None
    t = peek_token(tokens, i2)
    if left is not None and t is not None and isinstance(t, T_OP) and t.s in ["==", "!=", "<", ">", "<=", ">="]:
        op = t.s
        i2 += 1
        right, i2 = parse_aexp(tokens, i2)
        return Bop(op, left, right), i2

    # try logical operators that require a parenthesized BExp.
    # this covers alternatives like: ( BExp ) && BExp  and ( BExp ) || BExp.
    matched, i2 = match_paren(tokens, orig_i, "(")
    if matched:
        inner, i2 = parse_bexp(tokens, i2)
        matched2, i2 = match_paren(tokens, i2, ")")
        if not matched2:
            raise ParseError("Missing ')' in BExp at position %d" % i2)
        # check for && or || immediately following the parenthesized BExp.
        t = peek_token(tokens, i2)
        if t is not None and isinstance(t, T_OP) and t.s in ["&&", "||"]:
            op = t.s
            i2 += 1
            right, i2 = parse_bexp(tokens, i2)
            return Lop(op, inner, right), i2
        # otherwise, just return the parenthesized boolean.
        return inner, i2

    # try boolean constants
    t = peek_token(tokens, orig_i)
    if t is not None and isinstance(t, T_KEYWORD):
        if t.s == "true":
            return TrueConst(), orig_i+1
        elif t.s == "false":
            return FalseConst(), orig_i+1

    # try a plain parenthesized boolean expression.
    matched, i2 = match_paren(tokens, orig_i, "(")
    if matched:
        inner, i2 = parse_bexp(tokens, i2)
        matched2, i2 = match_paren(tokens, i2, ")")
        if not matched2:
            raise ParseError("Missing ')' in BExp at position %d" % i2)
        return inner, i2

    raise ParseError("Invalid BExp at position %d" % orig_i)


# simple statements compund statements and blocks

def parse_stmt(tokens, i):
    """
    Stmt -> 
        'skip'
      | T_ID ':=' AExp
      | 'if' BExp 'then' Block 'else' Block
      | 'while' BExp 'do' Block
      | 'write' T_ID
      | 'write' T_STRING
      | 'write' '(' T_ID ')'       
      | 'write' '(' T_STRING ')'  
      | 'read'  T_ID
    """
    # skip
    matched, i2 = match_keyword(tokens, i, "skip")
    if matched:
        return Skip(), i2

    # if T_ID => parse assign
    t = peek_token(tokens, i)
    if isinstance(t, T_ID):
        varname, i2 = match_id(tokens, i)
        # next token must be T_OP(":=")
        matchedOp, i3 = match_op(tokens, i2, ":=")
        if matchedOp:
            a, i4 = parse_aexp(tokens, i3)
            return Assign(varname, a), i4
        # if it's not ':=', we proceed to an error
        raise ParseError("Expected ':=' after ID at position %d" % i2)

    # if ... then ... else ...
    matched, i2 = match_keyword(tokens, i, "if")
    if matched:
        bexp, i2 = parse_bexp(tokens, i2)
        matched2, i2 = match_keyword(tokens, i2, "then")
        if not matched2:
            raise ParseError("Expected 'then' in if-statement at position %d" % i2)
        block_then, i2 = parse_block(tokens, i2)
        matched3, i2 = match_keyword(tokens, i2, "else")
        if not matched3:
            raise ParseError("Expected 'else' in if-statement at position %d" % i2)
        block_else, i2 = parse_block(tokens, i2)
        return If(bexp, block_then, block_else), i2

    # while ... do ...
    matched, i2 = match_keyword(tokens, i, "while")
    if matched:
        bexp, i2 = parse_bexp(tokens, i2)
        matched2, i2 = match_keyword(tokens, i2, "do")
        if not matched2:
            raise ParseError("Expected 'do' in while-statement at position %d" % i2)
        block_st, i2 = parse_block(tokens, i2)
        return While(bexp, block_st), i2

    # read ID
    matched, i2 = match_keyword(tokens, i, "read")
    if matched:
        varname, i2 = match_id(tokens, i2)
        return Read(varname), i2

    # write ...
    matched, i2 = match_keyword(tokens, i, "write")
    if matched:
        # check if next is T_ID or T_STRING or '(' T_ID ')' or '(' T_STRING ')'
        t2 = peek_token(tokens, i2)
        if isinstance(t2, T_ID):
            varname, i3 = match_id(tokens, i2)
            return WriteId(varname), i3
        elif isinstance(t2, T_STRING):
            txt, i3 = match_string(tokens, i2)
            return WriteString(txt), i3
        elif isinstance(t2, T_PAREN) and t2.s == "(":
            # skip '('
            _, i3 = match_paren(tokens, i2, "(")
            # next could be ID or STRING
            t3 = peek_token(tokens, i3)
            if isinstance(t3, T_ID):
                varname, i4 = match_id(tokens, i3)
                # expect ')'
                matched3, i5 = match_paren(tokens, i4, ")")
                if not matched3:
                    raise ParseError("Missing ')' after write( ID ) at %d" % i4)
                return WriteId(varname), i5
            elif isinstance(t3, T_STRING):
                txt, i4 = match_string(tokens, i3)
                matched3, i5 = match_paren(tokens, i4, ")")
                if not matched3:
                    raise ParseError("Missing ')' after write( STRING ) at %d" % i4)
                return WriteString(txt), i5
            else:
                raise ParseError("Expected ID or STRING after 'write(' at position %d" % i3)
        else:
            raise ParseError("Expected ID or STRING after 'write' at position %d" % i2)

    # if we reach here, no statement matched
    raise ParseError("Invalid statement at position %d" % i)

def parse_stmts(tokens, i):
    """
    Stmts -> Stmt ';' Stmts
           | Stmt
    """
    stmt, i2 = parse_stmt(tokens, i)
    # check if next token is ';'
    matched, i3 = match_semi(tokens, i2)
    if matched:
        # parse more statements
        rest, i4 = parse_stmts(tokens, i3)
        # combine them into a list
        return [stmt] + rest, i4
    else:
        # just one statement
        return [stmt], i2

def parse_block(tokens, i):
    """
    Block -> '{' Stmts '}'
           | Stmt
    """
    # check if next token is '{'
    matched, i2 = match_paren(tokens, i, "{")
    if matched:
        # parse statements
        stmts, i3 = parse_stmts(tokens, i2)
        # expect '}'
        matched2, i4 = match_paren(tokens, i3, "}")
        if not matched2:
            raise ParseError("Missing '}' for block at position %d" % i3)
        return stmts, i4

    # else parse single statement as a block of length 1
    stmt, i2 = parse_stmt(tokens, i)
    return [stmt], i2

# Parse the entire program

import time

def parse_program(tokens):
    """
    Parse the entire token list as a "block" (or list of statements).
    Return the AST (list of statements). 
    """
    start = time.time()
    block, i = parse_stmts(tokens, 0)
    if i != len(tokens):
        raise ParseError("Extra tokens after valid parse at position %d" % i)
    end = time.time()
    print("Parsed: ")
    print(block)
    print("Parsing time taken: "+ str(end - start) + " seconds")
    return block