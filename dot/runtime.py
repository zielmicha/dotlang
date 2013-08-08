from dot.lib.core import builtins

def call(a, b):
    return NotImplemented

def execute(executable):
    globals = {'__builtins__': builtins}
    return eval(executable, globals)

builtins['_dotlang_call'] = call
