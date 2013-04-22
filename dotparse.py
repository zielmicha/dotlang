#!/usr/bin/python
import re

class TokenizeError(Exception): pass

class Tokenizer:
    def __init__(self, tokens):
        self.tokens = [ (ident, re.compile('^' + token, re.MULTILINE)) for ident, token in tokens ]

    def tokenize(self, string, start=0):
        # complexity: len(tokentypes) * len(string)**2

        lineno = 1
        while string:
            match = None
            for ident, exp in self.tokens:
                m = exp.match(string)
                if m:
                    match_text = m.group(0)
                    string = string[len(match_text):]
                    match = (ident, match_text, lineno)
                    lineno += match_text.count('\n')
                    break
            if not match:
                raise TokenizeError('failed to tokenize %r' % string)
            yield match

def gen_as_list(func):
    def wrapper(*args, **kwargs):
        return list(func(*args, **kwargs))
    return wrapper

dot_tokenizer = Tokenizer([
    ('paren', r'[(){}]'),
    ('space', r'[ \t]+'),
    ('newline', r'\n'),
    ('ident', r'[.A-Za-z0-9]+'),
    ('comment', r'(#(.+)$|/\*((.|\n)*?)\*/)'),
    ('string', r'"([^"]+)"'),
    ('semicolon', r';'),
    ('bar', r'\|'),
])

paren_map = dict(zip('({', ')}'))
group_kinds = ('expr', 'lambda', 'lambda_back')

class ParseError(Exception): pass

def fold_parens(tokens):
    root = []
    current = root
    stack = []
    for kind, val, info in tokens:
        if kind == 'paren':
            if val in paren_map: # opening
                stack.append(current)
                current = []
            else: # closing
                stack[-1].append(('paren', (val, current), info))
                current = stack.pop()
        else:
            current.append((kind, val, info))
    return root

@gen_as_list
def match_dots(tokens):
    is_dot = False
    for kind, val, info in tokens:
        if kind == 'paren':
            paren_type, inside = val
            newval = match_dots(inside)
            if is_dot:
                if paren_type != ')':
                    raise ParseError('not expecting dot before %r paren' % paren_type, info)
                yield ('lambda', newval, info)
                is_dot = False
            else:
                if paren_type == ')':
                    yield ('expr', newval, info)
                else:
                    yield ('lambda_back', newval, info)
        else:
            if is_dot:
                raise ParseError('not expecting dot before %r' % kind)
            if kind == 'ident':
                if val == '.':
                    is_dot = True
                if val.startswith('.'):
                    yield ('ref', val[1:], info)
                elif val.endswith('.'):
                    yield ('deref', val[:-1], info)
                else:
                    yield ('call', val, info)
            elif kind not in ('space', 'comment'):
                yield (kind, val, info)

def infer_semicolons(tokens):
    result = []
    for kind, val, info in tokens:
        if kind == 'newline':
            if result and result[-1][0] == 'call':
                result.append(('semicolon', val, info))
        elif kind == 'semicolon':
            if result and result[-1][0] != 'semicolon':
                result.append((kind, val, info))
        else:
            if kind in group_kinds:
                val = infer_semicolons(val)
            result.append((kind, val, info))
    if result[-1][0] == 'semicolon':
        del result[-1:]
    return result

def fold_bars(tokens):
    root = []
    current = root
    stack = []
    for kind, val, info in tokens:
        if kind == 'bar':
            stack.append(current)
            current = []
        elif kind == 'call':
            current.append((kind, val, info))
            if stack:
                stack[-1].append(('expr', current, info))
                current = stack.pop()
        else:
            if kind in group_kinds:
                val = fold_bars(val)
            current.append((kind, val, info))
    return root

def move_lambdas(tokens):
    result = []
    for kind, val, info in tokens:
        if kind == 'lambda_back':
            result.insert(-1, ('lambda', val, info))
        else:
            if kind in group_kinds:
                val = move_lambdas(val)
            result.append((kind, val, info))
    return result

def parse(text):
    return infer_semicolons(move_lambdas(fold_bars(match_dots(fold_parens(dot_tokenizer.tokenize(text))))))

if __name__ == '__main__':
    import sys, pprint
    r = parse(sys.stdin.read())
    pprint.pprint( r )
