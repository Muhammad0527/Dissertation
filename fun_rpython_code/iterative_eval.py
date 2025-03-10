from parser import Def, Main, Const, FConst, Num, FNum, ChConst, Var, Aop, If, Call, PrintString, Sequence, Bop
import os
import time
import math

def rpython_print(s):
    """Print a string to stdout without a new line."""
    os.write(1, s.encode('utf-8'))

def remove_quotes_and_convert_newlines(s):
    """
    RPython-friendly function that:
      - removes all double quotes
      - turns the two-character sequence \n into an actual newline
    """
    result_chars = []
    i = 0
    while i < len(s):
        c = s[i]
        if c == '\"':
            # Skip double quotes entirely
            i += 1
            continue
        if c == '\\' and i + 1 < len(s) and s[i+1] == 'n':
            result_chars.append('\n')
            i += 2
            continue
        result_chars.append(c)
        i += 1
    return ''.join(result_chars)

# Value classes for the environment
class Value(object):
    __slots__ = ()

class IntValue(Value):
    __slots__ = ('i',)
    def __init__(self, i):
        self.i = i

class FloatValue(Value):
    __slots__ = ('f',)
    def __init__(self, f):
        self.f = f

class StrValue(Value):
    __slots__ = ('s',)
    def __init__(self, s):
        self.s = s

class NoneValue(Value):
    """Represents a 'no value' or void return."""
    __slots__ = ()

# Function value classes
class FuncValue(Value):
    __slots__ = ()
    def call(self, arg_vals):
        raise Exception("FuncValue.call not implemented")

class BuiltinFunction(FuncValue):
    __slots__ = ('name',)
    def __init__(self, name):
        self.name = name
    def call(self, arg_vals):
        if self.name == 'skip':
            return NoneValue()
        elif self.name == 'print_int':
            if len(arg_vals) != 1:
                raise Exception("print_int expects 1 argument")
            x_val = arg_vals[0]
            if not isinstance(x_val, IntValue):
                raise Exception("print_int expected IntValue")
            rpython_print(str(x_val.i))
            return NoneValue()
        elif self.name == 'print_char':
            if len(arg_vals) != 1:
                raise Exception("print_char expects 1 argument")
            x_val = arg_vals[0]
            if not isinstance(x_val, IntValue):
                raise Exception("print_char expected IntValue")
            try:
                rpython_print(chr(x_val.i))
            except:
                rpython_print(str(x_val.i))
            return NoneValue()
        elif self.name == 'print_space':
            rpython_print(' ')
            return NoneValue()
        elif self.name == 'print_star':
            rpython_print('*')
            return NoneValue()
        elif self.name == 'new_line':
            rpython_print('\n')
            return NoneValue()
        else:
            raise Exception("Unknown built-in function: " + self.name)

class ClosureFunction(FuncValue):
    __slots__ = ('params', 'body', 'env')
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = env
    def call(self, arg_vals):
        if len(self.params) != len(arg_vals):
            raise Exception("Function expects %d arguments, got %d" % (len(self.params), len(arg_vals)))
        new_env = self.env.copy()
        for (param, _), arg in zip(self.params, arg_vals):
            new_env[param] = arg
        return iterative_eval(self.body, new_env)

# Iterative evaluator for expressions.
# It uses an explicit stack to simulate recursion.
def iterative_eval(exp, env):
    stack = []  # Stack holds continuation frames.
    current_expr = exp
    current_env = env
    current_result = None

    while True:
        if current_expr is not None:
            # Direct evaluation of base cases and operators.
            if isinstance(current_expr, Num):
                current_result = IntValue(current_expr.i)
                current_expr = None
            elif isinstance(current_expr, FNum):
                current_result = FloatValue(current_expr.f)
                current_expr = None
            elif isinstance(current_expr, ChConst):
                current_result = IntValue(current_expr.c)
                current_expr = None
            elif isinstance(current_expr, Var):
                if current_expr.s not in current_env:
                    raise Exception("Undefined variable: " + current_expr.s)
                current_result = current_env[current_expr.s]
                current_expr = None
            elif isinstance(current_expr, Aop):
                # Evaluate left operand; push frame to later apply op with right operand.
                stack.append(('aop', current_expr.op, current_expr.a2, current_env))
                current_expr = current_expr.a1
                continue
            elif isinstance(current_expr, Bop):
                # Evaluate left operand of boolean operator; save frame for right operand.
                stack.append(('bop', current_expr.op, current_expr.right, current_env))
                current_expr = current_expr.left
                continue
            elif isinstance(current_expr, If):
                # Evaluate condition (bexp), then later decide which branch to take.
                stack.append(('if', current_expr.e1, current_expr.e2, current_env))
                current_expr = current_expr.bexp
                continue
            elif isinstance(current_expr, Call):
                # Evaluate function arguments one-by-one.
                arg_exprs = current_expr.args
                stack.append(('call', current_expr.name, arg_exprs, 0, [], current_env))
                if len(arg_exprs) > 0:
                    current_expr = arg_exprs[0]
                    continue
                else:
                    current_result = None
                    current_expr = None
            elif isinstance(current_expr, PrintString):
                txt = remove_quotes_and_convert_newlines(current_expr.s)
                rpython_print(txt)
                current_result = NoneValue()
                current_expr = None
            elif isinstance(current_expr, Sequence):
                stack.append(('sequence', current_expr.e2, current_env))
                current_expr = current_expr.e1
                continue
            else:
                raise Exception("Unknown expression type: " + str(current_expr))
        
        # Process continuation frames if current_expr is None (i.e. sub-expression has been evaluated).
        if stack:
            frame = stack.pop()
            ftype = frame[0]
            if ftype == 'aop':
                # Frame format: ('aop', op, right_expr, saved_env)
                op = frame[1]
                right_expr = frame[2]
                saved_env = frame[3]
                left_result = current_result
                stack.append(('aop_apply', op, left_result))
                current_expr = right_expr
                current_env = saved_env
                continue
            elif ftype == 'aop_apply':
                # Frame format: ('aop_apply', op, left_result)
                op = frame[1]
                left_result = frame[2]
                right_result = current_result
                if isinstance(left_result, IntValue) and isinstance(right_result, IntValue):
                    l = left_result.i
                    r = right_result.i
                    if op == '+':
                        current_result = IntValue(l + r)
                    elif op == '-':
                        current_result = IntValue(l - r)
                    elif op == '*':
                        current_result = IntValue(l * r)
                    elif op == '/':
                        if r == 0:
                            raise Exception("Division by zero")
                        current_result = IntValue(l // r)
                    elif op == '%':
                        current_result = IntValue(l % r)
                    else:
                        raise Exception("Unknown operator: " + op)
                elif isinstance(left_result, FloatValue) and isinstance(right_result, FloatValue):
                    l = left_result.f
                    r = right_result.f
                    if op == '+':
                        current_result = FloatValue(l + r)
                    elif op == '-':
                        current_result = FloatValue(l - r)
                    elif op == '*':
                        current_result = FloatValue(l * r)
                    elif op == '/':
                        if r == 0.0:
                            raise Exception("Division by zero")
                        current_result = FloatValue(l / r)
                    elif op == '%':
                        current_result = FloatValue(math.fmod(l, r))
                    else:
                        raise Exception("Unknown operator: " + op)
                else:
                    raise Exception("Type mismatch in arithmetic")
                current_expr = None
                continue
            elif ftype == 'bop':
                # Frame format: ('bop', op, right_expr, saved_env)
                op = frame[1]
                right_expr = frame[2]
                saved_env = frame[3]
                left_result = current_result
                stack.append(('bop_apply', op, left_result))
                current_expr = right_expr
                current_env = saved_env
                continue
            elif ftype == 'bop_apply':
                # Frame format: ('bop_apply', op, left_result)
                op = frame[1]
                left_result = frame[2]
                right_result = current_result
                if isinstance(left_result, IntValue) and isinstance(right_result, IntValue):
                    l = left_result.i
                    r = right_result.i
                elif isinstance(left_result, FloatValue) and isinstance(right_result, FloatValue):
                    l = left_result.f
                    r = right_result.f
                else:
                    raise Exception("Type mismatch in boolean expression")
                if op == '==':
                    current_result = IntValue(1 if l == r else 0)
                elif op == '!=':
                    current_result = IntValue(1 if l != r else 0)
                elif op == '<':
                    current_result = IntValue(1 if l < r else 0)
                elif op == '>':
                    current_result = IntValue(1 if l > r else 0)
                elif op == '<=':
                    current_result = IntValue(1 if l <= r else 0)
                elif op == '>=':
                    current_result = IntValue(1 if l >= r else 0)
                else:
                    raise Exception("Unknown boolean operator: " + op)
                current_expr = None
                continue
            elif ftype == 'if':
                # Frame format: ('if', true_branch, false_branch, saved_env)
                true_branch = frame[1]
                false_branch = frame[2]
                saved_env = frame[3]
                cond_result = current_result
                if not isinstance(cond_result, IntValue):
                    raise Exception("Boolean expression must return IntValue (0 or 1)")
                if cond_result.i != 0:
                    current_expr = true_branch
                else:
                    current_expr = false_branch
                current_env = saved_env
                continue
            elif ftype == 'sequence':
                # Frame format: ('sequence', second_expr, saved_env)
                current_expr = frame[1]
                current_env = frame[2]
                continue
            elif ftype == 'call':
                # Frame format: ('call', func_name, arg_exprs, arg_index, eval_args, saved_env)
                func_name = frame[1]
                arg_exprs = frame[2]
                arg_index = frame[3]
                eval_args = frame[4]
                saved_env = frame[5]
                if len(arg_exprs) == 0:
                    # No arguments to evaluate; proceed directly
                    if func_name not in saved_env:
                        raise Exception("Undefined function: " + func_name)
                    func_val = saved_env[func_name]
                    if not isinstance(func_val, FuncValue):
                        raise Exception(func_name + " is not a function")
                    if isinstance(func_val, BuiltinFunction):
                        current_result = func_val.call(eval_args)
                        current_expr = None
                        current_env = saved_env
                        continue
                    elif isinstance(func_val, ClosureFunction):
                        if len(func_val.params) != len(eval_args):
                            raise Exception("Function expects %d arguments, got %d" % (len(func_val.params), len(eval_args)))
                        new_env = func_val.env.copy()
                        for (param, _), arg in zip(func_val.params, eval_args):
                            new_env[param] = arg
                        current_expr = func_val.body
                        current_env = new_env
                        continue
                    else:
                        raise Exception("Unknown function type for " + func_name)
                else:
                    eval_args.append(current_result)
                    arg_index += 1
                    if arg_index < len(arg_exprs):
                        stack.append(('call', func_name, arg_exprs, arg_index, eval_args, saved_env))
                        current_expr = arg_exprs[arg_index]
                        current_env = saved_env
                        continue
                    else:
                        if func_name not in saved_env:
                            raise Exception("Undefined function: " + func_name)
                        func_val = saved_env[func_name]
                        if not isinstance(func_val, FuncValue):
                            raise Exception(func_name + " is not a function")
                        if isinstance(func_val, BuiltinFunction):
                            current_result = func_val.call(eval_args)
                            current_expr = None
                            current_env = saved_env
                            continue
                        elif isinstance(func_val, ClosureFunction):
                            if len(func_val.params) != len(eval_args):
                                raise Exception("Function expects %d arguments, got %d" % (len(func_val.params), len(eval_args)))
                            new_env = func_val.env.copy()
                            for (param, _), arg in zip(func_val.params, eval_args):
                                new_env[param] = arg
                            current_expr = func_val.body
                            current_env = new_env
                            continue
                        else:
                            raise Exception("Unknown function type for " + func_name)
            else:
                raise Exception("Unknown frame type: " + str(ftype))
        else:
            # No more frames left; evaluation complete.
            return current_result

# Declaration evaluation (similar to recursive evaluator, but uses iterative_eval for Main)
def eval_decl(decl, env):
    if isinstance(decl, Const):
        env[decl.name] = IntValue(decl.value)
        return NoneValue()
    elif isinstance(decl, FConst):
        env[decl.name] = FloatValue(decl.value)
        return NoneValue()
    elif isinstance(decl, Def):
        env[decl.name] = NoneValue()
        closure = ClosureFunction(decl.args, decl.body, env)
        env[decl.name] = closure
        return NoneValue()
    elif isinstance(decl, Main):
        return iterative_eval(decl.body, env)
    else:
        raise Exception("Unknown declaration type: " + str(decl))

def iterative_interpret_program(decls):
    env = {
        'skip':        BuiltinFunction('skip'),
        'print_int':   BuiltinFunction('print_int'),
        'print_char':  BuiltinFunction('print_char'),
        'print_space': BuiltinFunction('print_space'),
        'print_star':  BuiltinFunction('print_star'),
        'new_line':    BuiltinFunction('new_line'),
    }
    result = NoneValue()
    i = 0
    while i < len(decls):
        res = eval_decl(decls[i], env)
        if not isinstance(res, NoneValue):
            result = res
        i += 1
    return result

def run(ast):
    start = time.time()
    result = iterative_interpret_program(ast)
    end = time.time()
    if isinstance(result, IntValue):
        rpython_print("Result: " + str(result.i) + "\n")
    elif isinstance(result, StrValue):
        rpython_print("Result: " + result.s + "\n")
    duration = end - start
    rpython_print("Evaluation Time: " + str(duration) + " seconds\n")