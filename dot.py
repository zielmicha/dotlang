#!/usr/bin/python
from dotlib import Environ, builtins, Ref, UserFunction

class StackFrame:
    def __init__(self, code, env, parent):
        self.env = env
        self.parent = parent
        self.stack = []
        self.code = code
        self.ptr = 0

    def step(self):
        if self.ptr == len(self.code):
            result = self.stack[-1] if self.stack else None
            self.parent.pass_result(result)
            return self.parent
        else:
            instr = self.code[self.ptr]
            self.ptr += 1
            try:
                return self.eval(*instr)
            except:
                print 'while evaluating', self.code[self.ptr-1]
                raise

    def eval(self, kind, val, info):
        if kind == 'string':
            self.stack.append(val.strip('"'))
            return self
        elif kind == 'call':
            func = self.env['func-' + val]
            args = self.stack[:]
            self.stack[:] = []
            return self.call(func, *args)
        elif kind == 'semicolon':
            self.stack[:] = []
            return self
        elif kind == 'ref':
            self.stack.append(Ref(self.env, val))
            return self
        elif kind == 'deref':
            v = self.env[val]
            self.stack.append(v)
            return self
        elif kind == 'number':
            self.stack.append(int(val))
            return self
        elif kind == 'lambda':
            self.stack.append(UserFunction(self.env, val))
            return self
        elif kind == 'expr':
            return StackFrame(val, self.env, self)
        else:
            raise RuntimeError(kind)

    def pass_result(self, v):
        self.stack.append(v)

    def call(self, func, *args):
        if isinstance(func, UserFunction):
            return StackFrame(func.code, func.env, self)
        else:
            result = func(*args)
            self.stack.append(result)
            return self

class RootFrame:
    def __init__(self, env, code):
        self.frame = StackFrame(code, env, self)

    def run(self):
        while self.frame != self:
            self.frame = self.frame.step()
        return self.result

    def pass_result(self, val):
        self.result = val

if __name__ == '__main__':
    from dotparse import parse
    from sys import stdin
    code = parse(stdin.read())
    RootFrame(Environ(parents=[builtins]), code).run()
