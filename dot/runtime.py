from dot.lib.core import builtins
from dot.lib import core

def call(a, b):
    return NotImplemented

def execute(executable):
    globals = {'__builtins__': builtins}
    return eval(executable, globals)

builtins['_dotlang_call'] = call
builtins['NotImplemented'] = NotImplemented

builtins['_dotlang_make_ref'] = core.BuiltinRef

def func_while(condition, body):
    while condition():
        body()

builtins['func-while'] = func_while

def _dotlang_arg(args, varnames):
    if len(args) != len(varnames):
        raise ValueError('function expected %d parameters (%s), got %d' %
                         (len(varnames), varnames, len(args)))

    return args

builtins['_dotlang_arg'] = _dotlang_arg

def func_if(cond, then, else_):
    if cond:
        return then()
    elif else_:
        return else_()

builtins['func-if'] = func_if
