
class Builder:
    def __init__(self, filename='<none>'):
        self.ops = []
        self.label_i = 0
        self.info = None
        self.stack_size = 0
        self.filename = filename

    def visit(self, ast):
        if isinstance(ast, list):
            for node in ast:
                self.visit(node)
        else:
            kind, val, info = ast
            self.info = info
            getattr(self, 'visit_' + kind)(val)

    def visit_string(self, s):
        self.add_push('const', s)

    def visit_call(self, name):
        stack = self.stack_size
        self.stack_size = 0
        self.add_push('call', name, stack)

    def visit_semicolon(self, _):
        for i in xrange(self.stack_size):
            self.add('pop')
        self.stack_size = 0

    def visit_ref(self, name):
        self.add_push('get_ref', name)

    def make_label(self, description='label'):
        self.label_i += 1
        return '%s_%d' % (description, label_i)

    def add_push(self, *args):
        self.stack_size += 1
        self.add(*args)

    def add(self, *args):
        self.ops.append((self.info, ) + args)

if __name__ == '__main__':
    from sys import argv, stdin
    from dot.parse import parse
    import pprint

    if len(argv) == 2:
        stdin = open(argv[1])

    ast = parse(stdin.read())
    b = Builder()
    b.visit(ast)
    pprint.pprint(b.ops)
