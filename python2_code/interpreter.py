from parser import If, While, Assign, Read, WriteId, WriteString, Var, Num, Aop, TrueConst, FalseConst, Bop, Lop, Skip

import sys
import time


def env_update(env, varname, value):
    """Update the environment with a new variable binding."""
    new_env = env.copy()
    new_env[varname] = value
    return new_env

# Arithmetic Expressions
def eval_aexp(aexp, env):
    """Evaluate an arithmetic expression under the given environment."""
    if isinstance(aexp, Var):
        return env[aexp.s]
    elif isinstance(aexp, Num):
        return aexp.i
    elif isinstance(aexp, Aop):
        op = aexp.op
        left = eval_aexp(aexp.left, env)
        right = eval_aexp(aexp.right, env)
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            return left // right  # integer division
        elif op == '%':
            return left % right
        else:
            raise Exception("Unknown arithmetic operator: " + op)
    else:
        raise Exception("Unknown arithmetic expression type: " + str(aexp))

# Boolean Expressions
def eval_bexp(bexp, env):
    """Evaluate a boolean expression under the given environment."""
    if isinstance(bexp, TrueConst):
        return True
    elif isinstance(bexp, FalseConst):
        return False
    elif isinstance(bexp, Bop):
        op = bexp.op
        left = eval_aexp(bexp.left, env)
        right = eval_aexp(bexp.right, env)
        if op == "==":
            return left == right
        elif op == "!=":
            return left != right
        elif op == "<":
            return left < right
        elif op == ">":
            return left > right
        elif op == "<=":
            return left <= right
        elif op == ">=":
            return left >= right
        else:
            raise Exception("Unknown relational operator: " + op)
    elif isinstance(bexp, Lop):
        op = bexp.op
        left_bool = eval_bexp(bexp.left, env)
        right_bool = eval_bexp(bexp.right, env)
        if op == "&&":
            return left_bool and right_bool
        elif op == "||":
            return left_bool or right_bool
        else:
            raise Exception("Unknown logical operator: " + op)
    else:
        raise Exception("Unknown boolean expression type: " + str(bexp))

# A Single Statement
def eval_stmt(stmt, env):
    """Evaluate a single statement under the given environment, returning a new environment."""
    if isinstance(stmt, Skip):
        return env

    elif isinstance(stmt, Assign):
        # Use stmt.varname and stmt.aexp
        return env_update(env, stmt.varname, eval_aexp(stmt.aexp, env))

    elif isinstance(stmt, Read):
        line = sys.stdin.readline().strip()
        try:
            value = int(line)
        except:
            raise Exception("Input is not a valid integer: " + line)
        return env_update(env, stmt.varname, value)

    elif isinstance(stmt, WriteId):
        sys.stdout.write(str(env[stmt.varname]))
        return env

    elif isinstance(stmt, WriteString):
        stext = stmt.text.replace("\"", "").replace("\\n", "\n")
        sys.stdout.write(stext)
        return env

    elif isinstance(stmt, If):
        if eval_bexp(stmt.bexp, env):
            return eval_block(stmt.block_then, env)
        else:
            return eval_block(stmt.block_else, env)

    elif isinstance(stmt, While):
        if eval_bexp(stmt.bexp, env):
            new_env = eval_block(stmt.block, env)
            return eval_stmt(stmt, new_env)
        else:
            return env

    else:
        raise Exception("Unknown statement type: " + str(stmt))

# A Block of Statements
def eval_block(block, env):
    """Evaluate a list of statements sequentially."""
    for stmt in block:
        env = eval_stmt(stmt, env)
    return env

# Top-Level Program Evaluation
def eval_program(block):
    """Evaluate the entire program from an empty environment."""
    return eval_block(block, {})

# Recursive Evaluation
import time

def run(ast):
    print("Eval:")
    start = time.time()
    final_env = eval_program(ast)
    end = time.time()
    print(str(final_env) + "\n")
    print("Recursive evaluation Time: " + str(end - start))
    return 0