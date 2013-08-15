from dot.lib.core import builtins
from dot.lib import core

import dot.compiler.builder
import dot.compiler.asm
import dot.parse

def call(a, b):
    return NotImplemented

def execute(executable):
    globals = {'__builtins__': builtins}
    return eval(executable, globals)

def execute_string(str, filename='<string>'):
    ast = dot.parse.parse(str)
    b = dot.compiler.builder.Builder(filename)
    b.add_code(ast)
    code = dot.compiler.asm.assemble(b).to_code()
    return execute(code)

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

def _dotlang_fallback(args, funcname):
    if funcname.startswith('@'):
        assert len(args) == 1
        return getattr(args[0], funcname[1:])
    else:
        try:
            func = getattr(args[0], funcname)
        except (AttributeError, IndexError):
            raise AttributeError('function %s not found' % funcname)
        else:
            return func(*args[1:])

builtins['_dotlang_fallback'] = _dotlang_fallback

def func_if(cond, then, else_):
    if cond:
        return then()
    elif else_:
        return else_()

builtins['func-if'] = func_if

builtins['tuple'] = tuple # for varargs conversions
