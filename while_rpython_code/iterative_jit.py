from parser import If, While, Assign, Read, WriteId, WriteString, Var, Num, Aop, TrueConst, FalseConst, Bop, Lop, Skip

import os
from rpython.rlib.jit import JitDriver, purefunction, elidable

# JIT configuration
def get_location(block_id, pc):
    return "block:%s pc:%s" % (block_id, pc)

jitdriver = JitDriver(
    greens=['block_id', 'pc'],  # Block identifier and program counter
    reds=['env', 'worklist'],   # Environment and worklist are mutable
    get_printable_location=get_location
)

def rpython_read_line():
    "Read a line from stdin"
    chars = []
    while True:
        c = os.read(0, 1)
        if not c or c == '\n':
            break
        chars.append(c)
    return "".join(chars)

def rpython_print(s):
    "Print a string to stdout without a new line"
    os.write(1, s)

@elidable
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
        # Check if we have a backslash followed by 'n'
        if c == '\\' and i + 1 < len(s) and s[i+1] == 'n':
            result_chars.append('\n')
            i += 2
            continue
        # Otherwise, keep the character
        result_chars.append(c)
        i += 1

    return "".join(result_chars)

def env_update(env, varname, value):
    """Update the environment with a new variable binding."""
    new_env = env.copy()
    new_env[varname] = value
    return new_env

# Iterative Evaluation of Arithmetic Expressions
@elidable
def eval_aexp_iterative(aexp, env):
    """
    Evaluate an arithmetic expression using an explicit stack.
    """
    # Each stack item is a tuple (node, visited_flag)
    stack = [(aexp, False)]
    result_stack = []
    while stack:
        node, visited = stack.pop()
        if isinstance(node, Var):
            result_stack.append(env[node.s])
        elif isinstance(node, Num):
            result_stack.append(node.i)
        elif isinstance(node, Aop):
            if not visited:
                # Postorder: push node back as visited, then push its children.
                stack.append((node, True))
                # Push right child first so that left child is processed first.
                stack.append((node.right, False))
                stack.append((node.left, False))
            else:
                right = result_stack.pop()
                left = result_stack.pop()
                op = node.op
                if op == '+':
                    result_stack.append(left + right)
                elif op == '-':
                    result_stack.append(left - right)
                elif op == '*':
                    result_stack.append(left * right)
                elif op == '/':
                    # Use integer division.
                    result_stack.append(left // right)
                elif op == '%':
                    result_stack.append(left % right)
                else:
                    raise Exception("Unknown arithmetic operator: " + op)
        else:
            raise Exception("Unknown arithmetic expression type: " + str(node))
    if len(result_stack) != 1:
        raise Exception("Arithmetic evaluation error: result stack not of size 1")
    return result_stack[0]

# Iterative Evaluation of Boolean Expressions
@elidable
def eval_bexp_iterative(bexp, env):
    """
    Evaluate a boolean expression using an explicit stack.
    For Bop nodes, the left and right children are arithmetic expressions and are evaluated
    using eval_aexp_iterative.
    """
    stack = [(bexp, False)]
    result_stack = []
    while stack:
        node, visited = stack.pop()
        if isinstance(node, Bop):
            # Directly evaluate the arithmetic subexpressions for left and right.
            op = node.op
            left = eval_aexp_iterative(node.left, env)
            right = eval_aexp_iterative(node.right, env)
            if op == "==":
                result_stack.append(left == right)
            elif op == "!=":
                result_stack.append(left != right)
            elif op == "<":
                result_stack.append(left < right)
            elif op == ">":
                result_stack.append(left > right)
            elif op == "<=":
                result_stack.append(left <= right)
            elif op == ">=":
                result_stack.append(left >= right)
            else:
                raise Exception("Unknown relational operator: " + op)
        elif isinstance(node, Lop):
            if not visited:
                # For logical operations, use a postorder traversal of children.
                stack.append((node, True))
                stack.append((node.right, False))
                stack.append((node.left, False))
            else:
                right = result_stack.pop()
                left = result_stack.pop()
                op = node.op
                if op == "&&":
                    result_stack.append(left and right)
                elif op == "||":
                    result_stack.append(left or right)
                else:
                    raise Exception("Unknown logical operator: " + op)
        elif isinstance(node, TrueConst):
            result_stack.append(True)
        elif isinstance(node, FalseConst):
            result_stack.append(False)
        else:
            raise Exception("Unknown boolean expression type: " + str(node))
    if len(result_stack) != 1:
        raise Exception("Boolean evaluation error: result stack not of size 1")
    return result_stack[0]

# Fully Iterative Statement Interpreter with JIT
def run_program_iterative(block, env):
    """
    Interpret a block of statements iteratively using an explicit worklist with JIT.
    The worklist is a list of statements to be executed.
    """
    # Copy the initial block into our worklist.
    worklist = block[:]  # list of statements to execute
    pc = 0  # "Program counter" for JIT
    block_id = 0  # Block identifier for JIT
    
    while worklist:
        jitdriver.jit_merge_point(block_id=block_id, pc=pc, env=env, worklist=worklist)
        
        if not worklist:
            break
            
        stmt = worklist.pop(0)  # fetch next statement in order
        pc += 1
        
        if isinstance(stmt, Skip):
            continue

        elif isinstance(stmt, Assign):
            value = eval_aexp_iterative(stmt.aexp, env)
            env = env_update(env, stmt.varname, value)

        elif isinstance(stmt, Read):
            line = rpython_read_line()
            try:
                value = int(line)
            except:
                raise Exception("Input is not a valid integer: " + line)
            env = env_update(env, stmt.varname, value)

        elif isinstance(stmt, WriteId):
            rpython_print(str(env[stmt.varname]))

        elif isinstance(stmt, WriteString):
            stext = remove_quotes_and_convert_newlines(stmt.text)
            rpython_print(stext)

        elif isinstance(stmt, If):
            cond = eval_bexp_iterative(stmt.bexp, env)
            if cond:
                # Prepend the 'then' block.
                worklist = stmt.block_then + worklist
                # New block ID for JIT
                block_id += 1
            else:
                # Prepend the 'else' block.
                worklist = stmt.block_else + worklist
                # New block ID for JIT
                block_id += 2

        elif isinstance(stmt, While):
            cond = eval_bexp_iterative(stmt.bexp, env)
            if cond:
                # To simulate a while loop, we prepend the loop body
                # followed by the while statement itself (to re-check the condition).
                worklist = stmt.block + [stmt] + worklist
                # This is a loop back, can enter JIT
                pc = 0  # Reset PC for the loop body
                jitdriver.can_enter_jit(block_id=block_id, pc=pc, env=env, worklist=worklist)
            else:
                # Exit the loop, increment block ID
                block_id += 1
        else:
            raise Exception("Unknown statement type: " + str(stmt))
    return env

# Iterative Evaluation of a Program
import time

def env_to_string(env):
    items = []
    for k, v in env.items():
        items.append(str(k) + ": " + str(v))
    return "{" + ", ".join(items) + "}"

def run(ast):
    print("Eval with JIT:")
    start = time.time()
    final_env = run_program_iterative(ast, {})
    end = time.time()
    print(env_to_string(final_env) + "\n")
    print("Evaluation Time: " + str(end - start) + "s")
    return 0