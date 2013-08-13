
class Builder:
    def __init__(self, filename='<none>', function=False):
        self.ops = []
        self.label_i = 0
        self.info = None
        self.stack_size = 0
        self.var_stack = True if function else False
        self.filename = filename
        self.names = None
        self.cells = None

    def add_code(self, ast):
        assert self.names is None, 'call add_code once'
        self.names, self.cells = find_names_and_cells(ast)
        self.visit(ast)

    def visit(self, ast):
        assert self.names is not None, 'call add_code, not visit'
        if isinstance(ast, list):
            for node in ast:
                self.visit(node)
        else:
            kind, val, info = ast
            self.info = info
            getattr(self, 'visit_' + kind)(val)

    def visit_string(self, s):
        self.add_push('const', s.strip('"'))

    def visit_number(self, n):
        self.add_push('const', n)

    def visit_call(self, name):
        stack = self.stack_size
        self.stack_size = 0
        self.add_push('call', name, stack, self.var_stack)
        self.var_stack = False

    def visit_semicolon(self, _):
        for i in xrange(self.stack_size):
            self.add('pop')
        self.stack_size = 0
        if self.var_stack:
            self.add('pop')
        self.var_stack = False

    def visit_ref(self, name):
        self.add_push('get_ref', name)

    def visit_deref(self, name):
        self.add_push('deref', name)

    def visit_expr(self, expr):
        old_stack_size = self.stack_size
        old_var_stack = self.var_stack
        self.var_stack = False
        self.stack_size = 0
        self.visit(expr)
        self.stack_size = old_stack_size
        self.var_stack = old_var_stack

    def visit_lambda(self, expr):
        lambda_builder = Builder(function=True)
        lambda_builder.filename = self.filename
        lambda_builder.add_code(expr)
        self.add_push('make_lambda', lambda_builder)

    def make_label(self, description='label'):
        self.label_i += 1
        return '%s_%d' % (description, label_i)

    def add_push(self, *args):
        self.stack_size += 1
        self.add(*args)

    def add(self, *args):
        self.ops.append((self.info, ) + args)

def find_names_and_cells(ast):
    names = []
    cells = []
    for kind, val, info in ast:
        if kind == 'ref':
            names.append(val)
        elif kind == 'deref':
            names.append(val)
            cells.append(val)
        elif kind in ('lambda', 'expr'):
            found = find_names(val)
            names += found
            cells += found
        elif kind == 'call':
            if val == 'arg':
                # new scope, discard this closure
                return [], []
            else:
                names.append('func-' + val)

    return names, cells

def find_names(ast):
    return find_names_and_cells(ast)[0]

if __name__ == '__main__':
    from sys import argv, stdin
    from dot.parse import parse
    import pprint

    if len(argv) == 2:
        stdin = open(argv[1])

    ast = parse(stdin.read())
    b = Builder()
    b.add_code(ast)
    pprint.pprint(b.ops)
