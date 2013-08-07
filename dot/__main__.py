from sys import argv

from dot.parse import parse
from dot.runtime import * # __main__ --> dot

def run_string(s):
    code = parse(s)
    return RootFrame(Environ(parents=[builtins]), code).run()

if len(argv) == 1:
    import traceback
    import os
    import readline
    histfile = os.path.join(os.path.expanduser("~"), ".dot_history")
    try:
        readline.read_history_file(histfile)
    except IOError:
        pass
    import atexit
    atexit.register(readline.write_history_file, histfile)
    del os, histfile

    while True:
        try:
            s = raw_input('> ')
        except (KeyboardInterrupt, EOFError):
            break
        try:
            print repr(run_string(s))
        except:
            traceback.print_exc()
else:
    stdin = open(argv[1])
    run_string(stdin.read())
