from lexer import (
    T_SEMI, T_COLON, T_COMMA, T_LPAREN, T_RPAREN,
    T_LBRACE, T_RBRACE, T_ID, T_TYPE, T_CONST, T_CHAR,
    T_STRING, T_OP, T_INT, T_DOUBLE, T_KWD
)
    
# AST Definitions

class Decl(object):
    __slots__ = ()

class Def(Decl):
    __slots__ = ('name', 'args', 'ty', 'body')

    def __init__(self, name, args, ty, body):
        self.name = name         
        self.args = args         
        self.ty = ty              
        self.body = body          
    def __repr__(self):
        return "Def(%s, %s, %s, %s)" % (self.name, self.args, self.ty, self.body.__repr__())

class Main(Decl):
    __slots__ = ('body',)

    def __init__(self, body):
        self.body = body

    def __repr__(self):
        return "Main(%s)" % (self.body.__repr__())

class Const(Decl):
    __slots__ = ('name', 'value')

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "Const(%s, %d)" % (self.name, self.value)

class FConst(Decl):
    __slots__ = ('name', 'value')

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "FConst(%s, %f)" % (self.name, self.value)


# Expressions and Boolean Expressions

class Exp(object):
    __slots__ = ()

class BExp(object):
    __slots__ = ()

class Var(Exp):
    __slots__ = ('s',)
    def __init__(self, s):
        self.s = s
    def __repr__(self):
        return "Var(%s)" % self.s

class Num(Exp):
    __slots__ = ('i',)
    def __init__(self, i):
        self.i = i
    def __repr__(self):
        return "Num(%d)" % self.i

class FNum(Exp):
    __slots__ = ('f',)
    def __init__(self, f):
        self.f = f
    def __repr__(self):
        return "FNum(%f)" % self.f

class ChConst(Exp):
    __slots__ = ('c',)
    def __init__(self, c):
        self.c = c
    def __repr__(self):
        return "ChConst(%s)" % str(self.c)

class Aop(Exp):
    __slots__ = ('op', 'a1', 'a2')

    def __init__(self, op, a1, a2):
        self.op = op      
        self.a1 = a1      
        self.a2 = a2      

    def __repr__(self):
        return "Aop(" + self.op + ", " + self.a1.__repr__() + ", " + self.a2.__repr__() + ")"

class Sequence(Exp):
    __slots__ = ('e1', 'e2')

    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

    def __repr__(self):
        return "Sequence(" + self.e1.__repr__() + ", " + self.e2.__repr__() + ")"

class PrintString(Exp):
    __slots__ = ('s',)

    def __init__(self, s):
        self.s = s

    def __repr__(self):
        return 'PrintString("%s")' % self.s

class Call(Exp):
    __slots__ = ('name', 'args')

    def __init__(self, name, args):
        self.name = name  
        self.args = args  

    def __repr__(self):
        args_str = ", ".join([arg.__repr__() for arg in self.args])
        return "Call(" + self.name + ", (" + args_str + "))"

class If(Exp):
    __slots__ = ('bexp', 'e1', 'e2')

    def __init__(self, bexp, e1, e2):
        self.bexp = bexp  
        self.e1 = e1      
        self.e2 = e2     

    def __repr__(self):
        return "If(" + self.bexp.__repr__() + ", " + self.e1.__repr__() + ", " + self.e2.__repr__() + ")"

class Bop(BExp):
    __slots__ = ('op', 'left', 'right')

    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

    def __repr__(self):
        return "Bop(" + self.op + ", " + self.left.__repr__() + ", " + self.right.__repr__() + ")"


# Peek and Error Helpers

def peek_token(tks, i):
    """Return tks[i] if i in range, else None."""
    if i < len(tks):
        return tks[i]
    return None

def error_expected(msg, i):
    raise Exception("Parse error at token index %d: expected %s" % (i, msg))


# Parsing Block: block := '{' Exp '}' | Exp

def parse_Block(tks, i):
    t = peek_token(tks, i)

    if t is not None and isinstance(t, T_LBRACE):
        i2 = i + 1
        exp_node, i3 = parse_Exp(tks, i2)
        t2 = peek_token(tks, i3)
        if t2 is None or not isinstance(t2, T_RBRACE):
            error_expected("'}'", i3)
        return exp_node, i3 + 1
    
    else:
        return parse_Exp(tks, i)


# Parsing Block without allowing a trailing in-expression semicolon.
# Used for function bodies in definitions.
# block_no_seq := '{' Exp '}' | Exp_no_seq

def parse_Block_no_seq(tks, i):
    t = peek_token(tks, i)

    if t is not None and isinstance(t, T_LBRACE):
        i2 = i + 1
        exp_node, i3 = parse_Exp(tks, i2)  # inside braces, sequences are allowed
        t2 = peek_token(tks, i3)
        if t2 is None or not isinstance(t2, T_RBRACE):
            error_expected("'}'", i3)
        return exp_node, i3 + 1
    
    else:
        return parse_Exp_no_seq(tks, i)

# Parsing Expressions without consuming a trailing semicolon.

def parse_Exp_no_seq(tks, i):
    # Try "if" BExp "then" Block_no_seq "else" Block_no_seq
    t = peek_token(tks, i)

    if t and isinstance(t, T_KWD) and t.s == "if":
        i2 = i + 1
        cond_node, i3 = parse_BExp(tks, i2)
        then_t = peek_token(tks, i3)
        if not (then_t and isinstance(then_t, T_KWD) and then_t.s == "then"):
            error_expected("'then'", i3)
        i4 = i3 + 1
        then_blk, i5 = parse_Block_no_seq(tks, i4)
        else_t = peek_token(tks, i5)
        if not (else_t and isinstance(else_t, T_KWD) and else_t.s == "else"):
            error_expected("'else'", i5)
        i6 = i5 + 1
        else_blk, i7 = parse_Block_no_seq(tks, i6)
        return If(cond_node, then_blk, else_blk), i7
    
    # Otherwise, parse M (but do NOT try to consume a semicolon here)
    m_node, i_m = parse_M(tks, i)
    return m_node, i_m


# Parsing Boolean Expressions: BExp := Exp (op Exp) with boolean ops

def parse_BExp(tks, i):
    left_node, i2 = parse_Exp(tks, i)
    op_t = peek_token(tks, i2)

    if op_t and isinstance(op_t, T_OP) and op_t.s in ["==","!=","<",">","<=",">="]:
        i3 = i2 + 1
        right_node, i4 = parse_Exp(tks, i3)
        return Bop(op_t.s, left_node, right_node), i4
    
    error_expected("a boolean operator (==, !=, <, >, <=, >=)", i2)
    return None, i2


# Helper for Backtracking: Try to parse an expression in an in-expression context.
# Returns a tuple: (success_flag, parsed_expression, new_index)

def try_parse_in_expr(tks, i):
    original_i = i

    try:
        expr, new_i = parse_Exp(tks, i)
        return True, expr, new_i
    except Exception:
        return False, None, original_i


# Parsing Expressions: Exp := "if" BExp "then" Block "else" Block
#                      | M ";" Exp
#                      | M

def parse_Exp(tks, i):
    # Try "if" BExp "then" Block "else" Block
    t = peek_token(tks, i)

    if t and isinstance(t, T_KWD) and t.s == "if":
        i2 = i + 1
        cond_node, i3 = parse_BExp(tks, i2)
        then_t = peek_token(tks, i3)
        if not (then_t and isinstance(then_t, T_KWD) and then_t.s == "then"):
            error_expected("'then'", i3)
        i4 = i3 + 1
        then_blk, i5 = parse_Block(tks, i4)
        else_t = peek_token(tks, i5)
        if not (else_t and isinstance(else_t, T_KWD) and else_t.s == "else"):
            error_expected("'else'", i5)
        i6 = i5 + 1
        else_blk, i7 = parse_Block(tks, i6)
        return If(cond_node, then_blk, else_blk), i7

    # Otherwise, parse M
    m_node, i_m = parse_M(tks, i)
    sem_t = peek_token(tks, i_m)
    if sem_t and isinstance(sem_t, T_SEMI):
        # Attempt to parse an expression after the semicolon as an in-expression.
        success, next_expr, new_i = try_parse_in_expr(tks, i_m + 1)
        if success:
            # If successful, interpret as Sequence(M, Exp)
            return Sequence(m_node, next_expr), new_i
        else:
            # Otherwise, treat the semicolon as top-level (do not consume it here)
            return m_node, i_m
    # If no semicolon (or if it shouldn't be in-expression), just return M
    return m_node, i_m


# Parsing M (basic expressions that can be part of an expression)
# M := "print_string" "(" StringParser ")" | L

def parse_M(tks, i):
    t = peek_token(tks, i)

    if t and isinstance(t, T_ID) and t.s == "print_string":
        i2 = i + 1
        lp = peek_token(tks, i2)
        if not (lp and isinstance(lp, T_LPAREN)):
            error_expected("'(' after print_string", i2)
        i3 = i2 + 1
        s_token = peek_token(tks, i3)
        if not (s_token and isinstance(s_token, T_STRING)):
            error_expected("string-literal", i3)
        i4 = i3 + 1
        rp = peek_token(tks, i4)
        if not (rp and isinstance(rp, T_RPAREN)):
            error_expected("')' after string", i4)
        i5 = i4 + 1
        return PrintString(s_token.s), i5
    
    return parse_L(tks, i)


# Parsing L: L := T ("+" | "-") Exp | T

def parse_L(tks, i):
    left_node, i2 = parse_T(tks, i)
    op_t = peek_token(tks, i2)

    if op_t and isinstance(op_t, T_OP) and op_t.s in ["+","-"]:
        i3 = i2 + 1
        right_node, i4 = parse_Exp(tks, i3)
        return Aop(op_t.s, left_node, right_node), i4
    
    return left_node, i2


# Parsing T: T := F ("*" | "/" | "%") T | F

def parse_T(tks, i):
    left_node, i2 = parse_F(tks, i)
    op_t = peek_token(tks, i2)

    if op_t and isinstance(op_t, T_OP) and op_t.s in ["*","/","%"]:
        i3 = i2 + 1
        right_node, i4 = parse_T(tks, i3)
        return Aop(op_t.s, left_node, right_node), i4
    return left_node, i2


# Parsing F: F := Id "(" ")" | Id "(" ArgList ")" | "(" Exp ")"
#       | Id | Int | Double | Char

def parse_F(tks, i):
    t = peek_token(tks, i)

    if t and isinstance(t, T_ID):
        func_name = t.s
        i2 = i + 1
        maybe_lp = peek_token(tks, i2)
        if maybe_lp and isinstance(maybe_lp, T_LPAREN):
            i3 = i2 + 1
            maybe_rp = peek_token(tks, i3)
            if maybe_rp and isinstance(maybe_rp, T_RPAREN):
                return Call(func_name, []), i3 + 1
            else:
                args, i_after_args = parse_ArgList(tks, i3)
                closep = peek_token(tks, i_after_args)
                if not (closep and isinstance(closep, T_RPAREN)):
                    error_expected("')'", i_after_args)
                return Call(func_name, args), i_after_args + 1
        else:
            if func_name == "skip":
                return Call("skip", []), i2
            return Var(func_name), i2
        
    elif t and isinstance(t, T_CONST):
        const_name = t.s
        return Var(const_name), i + 1
    
    elif t and isinstance(t, T_LPAREN):
        i2 = i + 1
        subexp, i3 = parse_Exp(tks, i2)
        rp = peek_token(tks, i3)
        if not (rp and isinstance(rp, T_RPAREN)):
            error_expected("')'", i3)
        return subexp, i3 + 1
    
    elif t and isinstance(t, T_INT):
        node = Num(t.n)
        return node, i + 1
    
    elif t and isinstance(t, T_DOUBLE):
        node = FNum(t.n)
        return node, i + 1
    
    elif t and isinstance(t, T_CHAR):
        node = ChConst(t.c)
        return node, i + 1
    
    error_expected("a factor (identifier, literal, '('Exp')', etc.)", i)
    return None, i


# Parsing ArgList: one or more Exp separated by commas

def parse_ArgList(tks, i):
    first_node, i2 = parse_Exp(tks, i)
    args = [first_node]

    while True:
        t = peek_token(tks, i2)
        if t and isinstance(t, T_COMMA):
            i2 += 1
            next_exp, i2 = parse_Exp(tks, i2)
            args.append(next_exp)
        else:
            break

    return args, i2


# Parsing ParamList: parse function parameters (e.g. name : Type, ...)

def parse_ParamList(tks, i):
    params = []
    first_id, i2 = parse_IdTypePair(tks, i)
    params.append(first_id)

    while True:
        t = peek_token(tks, i2)
        if t and isinstance(t, T_COMMA):
            i2 += 1
            next_pair, i2 = parse_IdTypePair(tks, i2)
            params.append(next_pair)
        else:
            break

    return params, i2

def parse_IdTypePair(tks, i):
    t_id = peek_token(tks, i)

    if not (t_id and isinstance(t_id, T_ID)):
        error_expected("identifier in parameter list", i)

    i2 = i + 1
    c = peek_token(tks, i2)

    if not (c and isinstance(c, T_COLON)):
        error_expected("':' in parameter list", i2)

    i3 = i2 + 1
    ty_t = peek_token(tks, i3)

    if not (ty_t and isinstance(ty_t, T_TYPE)):
        error_expected("type in parameter list", i3)

    return (t_id.s, ty_t.s), i3 + 1


# Parsing Definitions: Defn := def ... or val ...

def parse_Defn(tks, i):
    kw = peek_token(tks, i)
    if not (kw and isinstance(kw, T_KWD) and kw.s in ["def","val"]):
        return False, i, None
    
    if kw.s == "def":
        i2 = i + 1
        name_t = peek_token(tks, i2)
        if not (name_t and isinstance(name_t, T_ID)):
            error_expected("identifier after 'def'", i2)
        func_name = name_t.s
        i3 = i2 + 1
        lp = peek_token(tks, i3)
        if not (lp and isinstance(lp, T_LPAREN)):
            error_expected("'(' after def name", i3)
        i4 = i3 + 1
        rp = peek_token(tks, i4)
        params = []
        i5 = i4
        if rp and isinstance(rp, T_RPAREN):
            i6 = i4 + 1
        else:
            params, i5 = parse_ParamList(tks, i4)
            rp = peek_token(tks, i5)
            if not (rp and isinstance(rp, T_RPAREN)):
                error_expected("')' after parameter list", i5)
            i6 = i5 + 1
        c = peek_token(tks, i6)
        if not (c and isinstance(c, T_COLON)):
            error_expected("':' after param list", i6)
        i7 = i6 + 1
        ty_t = peek_token(tks, i7)
        if not (ty_t and isinstance(ty_t, T_TYPE)):
            error_expected("return type", i7)
        i8 = i7 + 1
        eq_t = peek_token(tks, i8)
        if not (eq_t and isinstance(eq_t, T_OP) and eq_t.s == "="):
            error_expected("'=' after return type", i8)
        i9 = i8 + 1
        # Use the new parse_Block_no_seq here so that the trailing semicolon is not consumed.
        body_node, i10 = parse_Block_no_seq(tks, i9)
        return True, i10, Def(func_name, params, ty_t.s, body_node)
    
    else:
        # "val" case
        i2 = i + 1
        cst = peek_token(tks, i2)
        if not (cst and isinstance(cst, T_CONST)):
            error_expected("constant name after 'val'", i2)
        name = cst.s
        i3 = i2 + 1
        col = peek_token(tks, i3)
        if not (col and isinstance(col, T_COLON)):
            error_expected("':' after constant name", i3)
        i4 = i3 + 1
        type_t = peek_token(tks, i4)
        if not (type_t and isinstance(type_t, T_TYPE) and type_t.s in ["Int","Double"]):
            error_expected("type 'Int' or 'Double'", i4)
        i5 = i4 + 1
        eq_t = peek_token(tks, i5)
        if not (eq_t and isinstance(eq_t, T_OP) and eq_t.s == "="):
            error_expected("'=' after val's type", i5)
        i6 = i5 + 1
        lit = peek_token(tks, i6)
        if not lit:
            error_expected("an integer or double literal", i6)
        if type_t.s == "Int":
            if not isinstance(lit, T_INT):
                error_expected("integer literal", i6)
            node = Const(name, lit.n)
            return True, i6 + 1, node
        else:
            if not isinstance(lit, T_DOUBLE):
                error_expected("double literal", i6)
            node = FConst(name, lit.n)
            return True, i6 + 1, node


# Parsing Programs: Prog := (Defn ";" Prog) | (Block mapped to Main)

def parse_Prog(tks, i):
    has_defn, i2, defn_node = parse_Defn(tks, i)
    if has_defn:
        # Expect a semicolon after a definition (top-level semicolon)
        sm = peek_token(tks, i2)
        if not (sm and isinstance(sm, T_SEMI)):
            error_expected("';' after declaration", i2)
        i3 = i2 + 1
        rest, i4 = parse_Prog(tks, i3)
        return [defn_node] + rest, i4
    else:
        block_node, iB = parse_Block(tks, i)
        return [Main(block_node)], iB

# Top-level parse function

import time

def print_ast(ast):
    s = "["
    first = True
    for node in ast:
        if not first:
            s += ", "
        else:
            first = False
        s += node.__repr__()
    s += "]"
    return s

def parse(tks):
    start = time.time()
    ast, i2 = parse_Prog(tks, 0)
    end = time.time()
    if i2 != len(tks):
        raise Exception("Extra tokens after program at index %d" % i2)
    print("AST:")
    print(print_ast(ast))
    print("Parse Time: " + str(end - start) + "s")
    return ast