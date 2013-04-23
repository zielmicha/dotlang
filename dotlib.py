
class Environ(object):
    def __init__(self, parents=[]):
        self.data = {}
        self.parents = parents

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]

        for env in self.parents:
            try:
                return env[key]
            except KeyError:
                pass

        raise KeyError(key)

    def __setitem__(self, key, val):
        self.data[key] = val

class Ref(object):
    def __init__(self, env, name):
        self.env = env
        self.name = name

    def __call__(self):
        return self.env[self.name]

    def set(self, val):
        self.env[self.name] = val

    def __repr__(self):
        return '<dotlib.Ref %r env=%r>' % (self.name, self.env)

builtins = {}

def func_print(*args):
    print ' '.join(map(str, args))

builtins['func-print'] = func_print

def reducer(a):
    return lambda *args: reduce(a, args)

builtins['func-add'] = reducer(lambda a, b: a + b)
builtins['func-mul'] = reducer(lambda a, b: a + b)

builtins['func-call'] = lambda *args: args[-1](*args[:-1])
builtins['func-set'] = lambda val, ref: ref.set(val)

def func_def(name, body):
    if isinstance(name, Ref):
        body.name = name.name
    name.set(body)

builtins['func-def'] = func_def

class UserFunction(object):
    def __init__(self, env, code):
        self.env = env
        self.code = code
        self.name = '<lambda>'

    def __repr__(self):
        return '<dotlib.UserFunction %r at %x>' % (self.name, id(self))
