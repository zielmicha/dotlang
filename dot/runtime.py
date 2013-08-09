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
