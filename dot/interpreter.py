import dot.lib.core

from dot.lib.core import Environ, Ref, UserFunction

builtins = dot.lib.core.builtins.copy()

class StackFrame:
    def __init__(self, code, env, parent):
        self.env = env
        self.parent = parent
        self.stack = []
        self.code = code
        self.ptr = 0
        self.call_size = 0

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
            return self.eval_call(val, info)
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

    def eval_call(self, val, info):
        try:
            func = self.env['func-' + val]
        except KeyError:
            func = self.function_not_found(val)
        args = self.stack[:]
        self.stack[:] = []
        return self.call(func, *args)

    def function_not_found(self, name):
        return self.env['func-func-not-found'](name)

    def pass_result(self, v):
        self.stack.append(v)

    def call(self, func, *args):
        if isinstance(func, UserFunction):
            frame = StackFrame.make_call(func, self, *args)
            return frame
        elif hasattr(func, 'call_with_frame'):
            result = func(self, *args)
            return result
        else:
            result = func(*args)
            self.stack.append(result)
            return self

    @staticmethod
    def make_call(func, parent, *args):
        frame = StackFrame(func.code, func.env, parent)
        frame.call_size = len(args)
        frame.stack += args
        return frame

class RootFrame:
    def __init__(self, env, code):
        self.frame = StackFrame(code, env, self)

    def run(self):
        while self.frame != self:
            self.frame = self.frame.step()
        return self.result

    def pass_result(self, val):
        self.result = val

class WhileFrame:
    call_with_frame = True

    def __init__(self, parent, cond, body):
        self.cond = cond
        self.body = body
        self.parent = parent
        self.cond_ran = False
        self.halt = False

    def step(self):
        if self.halt:
            return self.parent
        if self.cond_ran:
            self.cond_ran = False
            return StackFrame.make_call(self.body, self)
        else:
            self.cond_ran = True
            return StackFrame.make_call(self.cond, self)

    def pass_result(self, val):
        if self.cond_ran:
            if not val:
                self.halt = True

builtins['func-while'] = WhileFrame

def if_(frame, cond, then, else_=None):
    if cond:
        return StackFrame.make_call(then, frame)
    else:
        if else_:
            return StackFrame.make_call(else_, frame)
        else:
            return frame

if_.call_with_frame = True
builtins['func-if'] = if_

def arg(frame, *args):
    call_args = args[:frame.call_size]
    def_args = args[frame.call_size:]
    new_env = Environ(parents=[frame.env])
    assert all( isinstance(r, Ref) for r in def_args )
    def_args_corrected = [
        Ref(new_env, r.name) for r in def_args
    ]
    if len(def_args_corrected) != len(call_args):
        raise ValueError('function expected %d parameters, got %d' % (
            len(def_args_corrected), len(call_args)))
    for out, val in zip(def_args_corrected, call_args):
        out.set(val)
    frame.env = new_env
    return frame

arg.call_with_frame = True
builtins['func-arg'] = arg
