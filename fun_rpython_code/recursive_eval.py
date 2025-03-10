from parser import Def, Main, Const, FConst, Num, FNum, ChConst, Var, Aop, If, Call, PrintString, Sequence, Bop

import os
import time
import math

def rpython_print(s):
    """Print a string to stdout without a new line."""
    os.write(1, s)

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
        if c == '"':
            # Skip double quotes entirely
            i += 1
            continue
        if c == '\\' and i + 1 < len(s) and s[i+1] == 'n':
            result_chars.append('\n')
            i += 2
            continue
        result_chars.append(c)
        i += 1
    return "".join(result_chars)


# Value classes for the environment

class Value(object):
    """Base class for all values in the environment."""
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


# We store functions in the environment as one of these classes below:


class FuncValue(Value):
    """
    Parent class for all function-like objects.
    We define a common 'call' interface that BuiltinFunction and
    ClosureFunction will implement.
    """
    __slots__ = ()

    def call(self, arg_vals):
        # Must be overridden in subclasses.
        raise Exception("FuncValue.call not implemented")

class BuiltinFunction(FuncValue):
    """
    Encapsulates a built-in function by name, so we avoid
    storing raw Python callables in the environment.
    """
    __slots__ = ('name',)

    def __init__(self, name):
        self.name = name

    def call(self, arg_vals):
        """Dispatch to a built-in function by name."""
        if self.name == 'skip':
            # does nothing
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
            # Print the character corresponding to x_val.i if possible
            try:
                rpython_print(chr(x_val.i))
            except:
                # Fallback to printing its integer value if out-of-range
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
    """
    A user-defined function: a closure storing parameters, body, and
    the environment in which it was defined.
    """
    __slots__ = ('params', 'body', 'env')

    def __init__(self, params, body, env):
        # params is a list of (name, type) pairs
        self.params = params
        self.body = body
        self.env = env

    def call(self, arg_vals):
        """Call this user-defined closure with arg_vals."""
        if len(self.params) != len(arg_vals):
            raise Exception(
                "Function expects %d arguments, got %d"
                % (len(self.params), len(arg_vals))
            )
        # Create a new environment for the function call
        new_env = self.env.copy()
        idx = 0

        while idx < len(self.params):
            param_name, _ = self.params[idx]
            new_env[param_name] = arg_vals[idx]
            idx += 1

        # Evaluate body
        return eval_exp(self.body, new_env)


# Expression evaluation

def eval_exp(exp, env):
    """
    Evaluate an expression in the given environment.
    Always return a Value (IntValue, FloatValue, StrValue, NoneValue, etc.).
    """

    if isinstance(exp, Num):
        return IntValue(exp.i)

    elif isinstance(exp, FNum):
        return FloatValue(exp.f)

    elif isinstance(exp, ChConst):
        # Return an IntValue storing the character code
        return IntValue(exp.c)

    elif isinstance(exp, Var):
        if exp.s not in env:
            raise Exception("Undefined variable: " + exp.s)
        return env[exp.s]

    elif isinstance(exp, Aop):
        left_val = eval_exp(exp.a1, env)
        right_val = eval_exp(exp.a2, env)
        op = exp.op

        if isinstance(left_val, IntValue) and isinstance(right_val, IntValue):
            left = left_val.i
            right = right_val.i
            if op == '+':
                return IntValue(left + right)
            elif op == '-':
                return IntValue(left - right)
            elif op == '*':
                return IntValue(left * right)
            elif op == '/':
                if right == 0:
                    raise Exception("Division by zero")
                return IntValue(left // right)
            elif op == '%':
                return IntValue(left % right)
            else:
                raise Exception("Unknown operator: " + op)
            
        elif isinstance(left_val, FloatValue) and isinstance(right_val, FloatValue):
            left = left_val.f
            right = right_val.f
            if op == '+':
                return FloatValue(left + right)
            elif op == '-':
                return FloatValue(left - right)
            elif op == '*':
                return FloatValue(left * right)
            elif op == '/':
                if right == 0.0:
                    raise Exception("Division by zero")
                return FloatValue(left / right)
            elif op == '%':
                return FloatValue(math.fmod(left, right))
            else:
                raise Exception("Unknown operator: " + op)
        else:
            raise Exception("Type mismatch in arithmetic")

    elif isinstance(exp, If):
        cond_val = eval_bexp(exp.bexp, env)
        if not isinstance(cond_val, IntValue):
            raise Exception("Boolean expression must return IntValue (0 or 1)")
        if cond_val.i != 0:
            return eval_exp(exp.e1, env)
        else:
            return eval_exp(exp.e2, env)

    elif isinstance(exp, Call):
        # Evaluate arguments to Value
        arg_vals = []
        i = 0
        while i < len(exp.args):
            arg_vals.append(eval_exp(exp.args[i], env))
            i += 1
        # Now call the function
        if exp.name not in env:
            raise Exception("Undefined function: " + exp.name)
        func_val = env[exp.name]
        if not isinstance(func_val, FuncValue):
            raise Exception(exp.name + " is not a function")
        return func_val.call(arg_vals)

    elif isinstance(exp, PrintString):
        txt = remove_quotes_and_convert_newlines(exp.s)
        rpython_print(txt)
        return NoneValue()

    elif isinstance(exp, Sequence):
        eval_exp(exp.e1, env)  # discard result
        return eval_exp(exp.e2, env)

    else:
        raise Exception("Unknown expression type: " + str(exp))


# Boolean expression evaluation

def eval_bexp(bexp, env):
    left_val = eval_exp(bexp.left, env)
    right_val = eval_exp(bexp.right, env)

    if isinstance(left_val, IntValue) and isinstance(right_val, IntValue):
        left = left_val.i
        right = right_val.i
    elif isinstance(left_val, FloatValue) and isinstance(right_val, FloatValue):
        left = left_val.f
        right = right_val.f
    else:
        raise Exception("Boolean expression requires both operands to be of the same numeric type")
    
    op = bexp.op
    if op == '==':
        return IntValue(1 if left == right else 0)
    elif op == '!=':
        return IntValue(1 if left != right else 0)
    elif op == '<':
        return IntValue(1 if left < right else 0)
    elif op == '>':
        return IntValue(1 if left > right else 0)
    elif op == '<=':
        return IntValue(1 if left <= right else 0)
    elif op == '>=' or op == '=>':
        return IntValue(1 if left >= right else 0)
    else:
        raise Exception("Unknown boolean operator: " + op)


# Declaration evaluation

def eval_decl(decl, env):
    """
    Evaluate a declaration and update the environment.
    For Main, return the result of its expression (always a Value).
    """

    if isinstance(decl, Const):
        env[decl.name] = IntValue(decl.value)
        return NoneValue()

    elif isinstance(decl, FConst):
        env[decl.name] = FloatValue(decl.value)
        return NoneValue()

    elif isinstance(decl, Def):
        # Insert a placeholder first for recursion
        env[decl.name] = NoneValue()

        # Create a closure object for this user-defined function
        closure = ClosureFunction(decl.args, decl.body, env)
        env[decl.name] = closure
        return NoneValue()

    elif isinstance(decl, Main):
        return eval_exp(decl.body, env)

    else:
        raise Exception("Unknown declaration type: " + str(decl))

# Interpret a FUN program (list of declarations)

def interpret_program(decls):
    """
    Interpret a FUN program (list of declarations).
    Returns the last non-NoneValue result.
    """
    # Start with an environment containing built-in functions
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

#######################################################################

def run(ast):
    """
    Entry point to run a FUN program.
    Evaluate the AST, print the result if it's an IntValue or StrValue.
    """
    start = time.time()
    result = interpret_program(ast)
    end = time.time()

    # Print result if it's IntValue or StrValue
    if isinstance(result, IntValue):
        rpython_print("Result: " + str(result.i) + "\n")
    elif isinstance(result, StrValue):
        rpython_print("Result: " + result.s + "\n")

    duration = end - start
    rpython_print("Evaluation Time: " + str(duration) + " seconds\n")