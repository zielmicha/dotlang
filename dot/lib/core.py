from functools import partial
import operator

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

class BuiltinRef(object):
    def __init__(self, fget, fset):
        self.fget = fget
        self.fset = fset

    def __call__(self):
        return self.fget()

    def set(self, val):
        self.fset(val)

builtins = {}

def func_print(*args):
    print ' '.join(map(str, args))

builtins['func-print'] = func_print

def reducer(a):
    return lambda *args: reduce(a, args)

builtins['func-add'] = reducer(lambda a, b: a + b)
builtins['func-mul'] = reducer(lambda a, b: a * b)
builtins['func-sub'] = lambda a, b: a - b
builtins['func-neq'] = lambda a, b: a != b
builtins['func-eq'] = lambda a, b: a == b
builtins['func-leq'] = lambda a, b: a <= b
builtins['func-le'] = lambda a, b: a < b
builtins['func-geq'] = lambda a, b: a >= b
builtins['func-ge'] = lambda a, b: a > b
builtins['func-not'] = lambda a: not a

builtins['func-int'] = lambda x: int(x)
builtins['func-sum'] = sum
builtins['func-len'] = len
builtins['func-abs'] = abs
builtins['func-at'] = lambda x, val: x[val]

class AtRef(object):
    def __init__(self, x, key):
        self.x = x
        self.key = key

    def __call_(self):
        return self.x[key]

    def set(self, val):
        self.x[self.key] = val

builtins['func-atref'] = AtRef

builtins['func-call'] = lambda *args: args[-1](*args[:-1])
builtins['func-set'] = lambda val, ref: ref.set(val)
builtins['func-list'] = lambda *args: list(args)

def func_multi(arg, *funclist):
    # TODO: use streams
    # (streams are not yet implemented and I just come up with name)
    return map(lambda func: func(arg), funclist)

builtins['func-multi'] = func_multi

builtins['func-map'] = lambda *args: map(partial(args[-1]), *args[:-1])

def func_assert(a):
    assert a

builtins['func-assert'] = func_assert

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

    def __call__(self, *args):
        import dot.runtime
        frame = dot.runtime.RootFrame(self.env, self.code)
        frame.frame.stack += args
        return frame.run()

def func_not_found(name):
    if name.startswith('@'):
        return operator.attrgetter(name[1:])
    else:
        def helper(self, *args):
            try:
                target = getattr(self, name)
            except AttributeError:
                raise AttributeError('no function named %r' % name)
            return target(*args)
        return helper

builtins['func-func-not-found'] = func_not_found

def dollar_swap(frame, *args):
    frame.stack += reversed(args)
    return frame

dollar_swap.call_with_frame = True

def dollar_list(frame, items):
    frame.stack += list(items)
    return frame

dollar_list.call_with_frame = True

builtins['func-$swap'] = dollar_swap
builtins['func-$list'] = dollar_list