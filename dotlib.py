
class Environ:
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

builtins = {}

def func_print(*args):
    print ' '.join(map(str, args))

builtins['func-print'] = func_print
