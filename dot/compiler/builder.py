from dot.lib import core

class Builder:
    def __init__(self, filename='<none>', function=False,
                 toplevel_names=[], upper_names=[]):
        # mess
        self.ops = []
        self.label_i = 0
        self.info = None
        self.stack_size = 0
        self.var_stack = True if function else False
        self.filename = filename
        self.names = None
        self.cells = None
        self.function = function
        self.toplevel_names = toplevel_names
        self.upper_names = upper_names
        self.free_names = None
        self.ref_stack = []

    def add_code(self, ast):
        assert self.names is None, 'call add_code once'
        self.names, self.here_names, self.cells = find_names_and_cells(ast)
        if not self.function:
            self.toplevel_names += self.here_names
            # just for performance (really helps?)
            self.toplevel_names += core.builtins.keys()
        self.free_names = set(self.names) - set(self.toplevel_names)
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
        self.add_push('const', int(n))

    def visit_call(self, name):
        stack = self.stack_size
        if name == 'arg':
            self.stack_size = 0
            if len(self.ref_stack) != stack:
                raise ValueError('arg not expected here (or not given reference, stack=%d, refs=%s)' % (
                    stack, self.ref_stack))
            self.free_names = set(self.upper_names)
            self.free_names -= set(self.ref_stack)
            self.toplevel_names = set(self.toplevel_names) - set(self.ref_stack)
            self.free_names -= set(self.toplevel_names)
            # discard everything before
            self.ops = []
            self.add('call_arg', [ (ref, ref in self.cells) for ref in self.ref_stack ])
            self.var_stack = False
        elif name == '$list':
            if not stack:
                raise ValueError('cannot call $list on empty (or variable) stack')
            self.add('store_helper', '__unpack')
            if self.var_stack:
                self.add('merge_var_stack', stack - 1)
            else:
                self.add('make_var_stack', stack - 1)
            self.add('load_helper', '__unpack')
            self.add('merge_var_args_list')
            self.var_stack = True
            self.stack_size = 0
        else:
            self.stack_size = 0
            self.add_push('call', name, stack, self.var_stack,
                          name in self.toplevel_names)
            self.var_stack = False

    def visit_semicolon(self, _):
        for i in xrange(self.stack_size):
            self.add('pop')
        self.stack_size = 0
        if self.var_stack:
            self.add('pop')
        self.var_stack = False

    def visit_ref(self, name):
        self.ref_stack.append(name)
        self.add_push('get_ref', name, name in self.toplevel_names)

    def visit_deref(self, name):
        self.add_push('deref', name, name in self.toplevel_names,
                      name in self.cells)

    def visit_expr(self, expr):
        old_stack_size = self.stack_size
        old_var_stack = self.var_stack
        self.var_stack = False
        self.stack_size = 0
        self.visit(expr)
        self.stack_size += old_stack_size
        self.var_stack = old_var_stack

    def visit_lambda(self, expr):
        lambda_builder = Builder(function=True,
                                 toplevel_names=self.toplevel_names,
                                 upper_names=self.names)
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
    here_names = []
    for kind, val, info in ast:
        if kind == 'ref':
            names.append(val)
            here_names.append(val)
        elif kind == 'deref':
            names.append(val)
            here_names.append(val)
            cells.append(val)
        elif kind in ('lambda', 'expr'):
            found = find_names(val)
            names += found
            cells += found
        elif kind == 'call':
            if val == 'arg':
                # new scope, discard this closure
                # hmm...
                pass
            else:
                here_names.append(val)
                names.append('func-' + val)

    return names, here_names, cells

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
