from . import asm
from flask import Flask

import flask
import logging
import cgi
import byteplay as bp
import hashlib

app = Flask(__name__)

id_save = {}

def escape(v):
    val = cgi.escape(repr(v))
    if isinstance(v, bp.Label):
        color = 0x111111 + (mhash(v) % 0xDDDDDD)
        return '<font color=#%s>%s</font>' % (color, val)
    elif isinstance(v, bp.Opcode):
        color = 'black'
        if val.startswith(('POP_', 'ROT_')):
            color = '#cccccc'
        if v == bp.LOAD_CONST:
            return '<b>%s</b>' % val
        return '<font color=%s>%s</font>' % (color, val)
    elif v is None:
        return ''
    elif isinstance(v, bp.Code):
        id_save[id(v)] = v
        return '<a href="/%d">%s</a>' % (id(v), val)
    else:
        return val

def mhash(h):
    return int(hashlib.md5(repr(h)).hexdigest(), 16)

@app.route("/")
@app.route("/<ident>")
def hello(ident=0):
    code = bp_main if not ident else id_save[int(ident)]
    l = ['''
<!doctype html>
<meta charset=utf-8>
<pre>
Freevars: %s
''' % code.freevars]
    for op, attr in code.code:
        l.append('%s: %s\n' % (escape(op), escape(attr)))
    return ''.join(l)

if __name__ == '__main__':
    app.logger.addHandler(logging.StreamHandler())
    bp_main = asm.assemble_test_main()
    app.run(debug=0)
