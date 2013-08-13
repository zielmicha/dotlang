import byteplay as bp
import marshal
import types

def assemble(builder, function=False, freevars=[]):
    code_list = []

    if function:
        code_list += [(bp.LOAD_FAST, '__args')]

    last_lineno = 0
    first_lineno = None
    for op in builder.ops:
        lineno = op[0]
        if lineno > last_lineno:
            # Python doesn't allow decreasing lineno
            code_list.append((bp.SetLineno, lineno))
            last_lineno = lineno
            if not first_lineno:
                first_lineno = lineno
        name = op[1]

        res = globals()['assemble_' + name](*op[2:])
        code_list += res

    code_list.append((bp.RETURN_VALUE, None))
    return bp.Code(
        code=code_list,
        freevars=freevars,
        args=['__args'] if function else [],
        varargs=True if function else False,
        varkwargs=False,
        newlocals=True,
        name='function' if function else 'module',
        filename=builder.filename,
        firstlineno=first_lineno,
        docstring=None)

def assemble_const(s):
    return [(bp.LOAD_CONST, s)]

def assemble_pop():
    return [(bp.POP_TOP, None)]

def assemble_deref(name, toplevel, is_cell):
    if toplevel:
        return [(bp.LOAD_GLOBAL, name)]
    elif is_cell:
        return [(bp.LOAD_DEREF, name)]
    else:
        return [(bp.LOAD_FAST, name)]

def assemble_make_lambda(builder):
    freevars = list(builder.free_names)
    code = assemble(builder, function=True,
                    freevars=freevars)
    ops = []
    for name in freevars:
        ops.append((bp.LOAD_CLOSURE, name))
    ops += [(bp.BUILD_TUPLE, len(freevars)),
            (bp.LOAD_CONST, code),
            (bp.MAKE_CLOSURE, 0)]
    return ops

def assemble_get_ref(name, toplevel):
    get_code = bp.Code(
        code=[(bp.LOAD_GLOBAL if toplevel else bp.LOAD_DEREF, name),
              (bp.RETURN_VALUE, None)],
        freevars=[] if toplevel else [name],
        args=[], varargs=False, varkwargs=False,
        newlocals=False,
        name='get_ref__%s' % name,
        filename='?', firstlineno=0, docstring='')
    set_code = bp.Code(
        code=[(bp.LOAD_FAST, 'value'),
              (bp.STORE_GLOBAL if toplevel else bp.STORE_DEREF, name),
              (bp.LOAD_CONST, None),
              (bp.RETURN_VALUE, None)],
        freevars=[] if toplevel else [name],
        args=['value'], varargs=False, varkwargs=False,
        newlocals=False,
        name='set_ref__%s' % name,
        filename='?', firstlineno=0, docstring='')

    if toplevel:
        return [
            (bp.LOAD_GLOBAL, '_dotlang_make_ref'),
            (bp.LOAD_CONST, get_code),
            (bp.MAKE_FUNCTION, 0),
            (bp.LOAD_CONST, set_code),
            (bp.MAKE_FUNCTION, 0),
            (bp.CALL_FUNCTION, 2)]
    else:
        return [
            (bp.LOAD_GLOBAL, '_dotlang_make_ref'),
            (bp.LOAD_CLOSURE, name),
            (bp.BUILD_TUPLE, 1),
            (bp.LOAD_CONST, get_code),
            (bp.MAKE_CLOSURE, 0),
            (bp.LOAD_CLOSURE, name),
            (bp.BUILD_TUPLE, 1),
            (bp.LOAD_CONST, set_code),
            (bp.MAKE_CLOSURE, 0),
            (bp.CALL_FUNCTION, 2)]

def assemble_call(name, arg_count, var_stack, toplevel):
    call_success = bp.Label()
    end = bp.Label()
    ops = [(bp.BUILD_TUPLE, arg_count),]
    if var_stack:
        ops += [(bp.BINARY_ADD, None)]
    ops += [(bp.LOAD_NAME, 'func-' + name),
            # stack = [args, func]
            (bp.ROT_TWO, None),
            # stack = [func, args]
            (bp.CALL_FUNCTION_VAR, 0),
        ]
    return ops

def assemble_call_arg(refs):
    ops = [
        (bp.LOAD_CONST, refs),
        (bp.LOAD_NAME, '_dotlang_arg'),
        (bp.ROT_THREE, None),
        (bp.CALL_FUNCTION, 2),
        (bp.UNPACK_SEQUENCE, len(refs))]
    for name, is_cell in refs:
        ops.append((bp.STORE_DEREF if is_cell else bp.STORE_FAST, name))
    return ops

def dump_pyc(py_code):
    magic = '\x03\xf3\r\n'
    timestamp = '\0\0\0\0'
    return magic + timestamp + marshal.dumps(py_code)

if __name__ == '__main__':
    from sys import argv, stdin
    import dot.parse
    import dot.compiler.builder
    import dot.runtime

    import pprint

    filename = '<stdin>'
    if len(argv) == 2:
        stdin = open(argv[1])
        filename = argv[1]

    ast = dot.parse.parse(stdin.read())
    b = dot.compiler.builder.Builder(filename)
    b.add_code(ast)
    bp_code = assemble(b)
    #pprint.pprint(bp_code.code[9][1].freevars)
    py_code = bp_code.to_code()
    dot.runtime.execute(py_code)
