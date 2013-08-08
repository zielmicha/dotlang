import byteplay as bp

def assemble(builder):
    code_list = []

    last_lineno = 0
    for op in builder.ops:
        lineno = op[0]
        if lineno != last_lineno:
            code_list.append((bp.SetLineno, lineno))
            last_lineno = lineno
        name = op[1]

        res = globals()['assemble_' + name](*op[2:])
        code_list += res

    code_list.append((bp.RETURN_VALUE, None))
    return bp.Code(
        code=code_list,
        freevars={},
        args=[],
        varargs=False,
        varkwargs=False,
        newlocals=True,
        name='dotlang',
        filename=builder.filename,
        firstlineno=0,
        docstring=None)

def assemble_const(s):
    return [(bp.LOAD_CONST, s)]

def assemble_call(name, arg_count):
    call_success = bp.Label()
    end = bp.Label()
    return [(bp.BUILD_TUPLE, arg_count),
            # stack = [args]
            (bp.DUP_TOP, None),
            # stack = [args, args]
            (bp.LOAD_GLOBAL, '_dotlang_call'),
            (bp.ROT_TWO, None),
            # stack = [args, _dotlang_call, args]
            (bp.LOAD_CONST, name),
            # stack = [args, _dotlang_call, args, name]
            (bp.CALL_FUNCTION, 2),
            # stack = [args, result]
            (bp.DUP_TOP, None),
            # stack = [args, result, result]
            (bp.LOAD_CONST, NotImplemented),
            # stack = [args, result, result, NotImplemented]
            (bp.COMPARE_OP, 'is'),
            # stack = [args, result, success?]
            (bp.POP_JUMP_IF_FALSE, call_success),
            # stack = [args, result]
            (bp.POP_TOP, None),
            # stack = [args]
            (bp.LOAD_GLOBAL, 'func-' + name),
            # stack = [args, func]
            (bp.ROT_TWO, None),
            # stack = [func, args]
            (bp.CALL_FUNCTION_VAR, 0),
            # stack = [result]
            (bp.JUMP_FORWARD, end),
            (call_success, None),
            # stack = [args, result]
            (bp.ROT_TWO, None),
            (bp.POP_TOP, None),
            # stack = [result]
            (end, None),
        ]

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
    b.visit(ast)
    bp_code = assemble(b)
    #print bp_code.code
    py_code = bp_code.to_code()
    dot.runtime.execute(py_code)
