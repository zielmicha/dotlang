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
    return [(bp.BUILD_TUPLE, arg_count),
            (bp.LOAD_GLOBAL, '_dotlang_call'),
#            (bp.ROT_TWO, None),
            (bp.LOAD_CONST, name),
            (bp.CALL_FUNCTION, 2)]

if __name__ == '__main__':
    from sys import argv, stdin
    from dot.parse import parse
    from dot.compiler.builder import Builder
    import pprint

    filename = '<stdin>'
    if len(argv) == 2:
        stdin = open(argv[1])
        filename = argv[1]

    ast = parse(stdin.read())
    b = Builder(filename)
    b.visit(ast)
    bp_code = assemble(b)
    print bp_code.code
    py_code = bp_code.to_code()
    exec py_code
