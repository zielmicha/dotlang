from dot.parse import parse

import os
import sys

if os.environ.get('DOTLANG_INTERPRETED'):
    from dot.interpreter import RootFrame, Environ, builtins
    def run_string(s):
        code = parse(s)
        return RootFrame(Environ(parents=[builtins]), code).run()
else:
    from dot.runtime import execute_string as run_string

def repl():
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
        if not s.strip():
            continue
        try:
            print repr(run_string(s))
        except:
            exc_type, exc_value, exc_tb = sys.exc_info()
            exc_tb = skip_frames(exc_tb, 3)
            traceback.print_exception(exc_type, exc_value, exc_tb)
    print

def skip_frames(tb, count):
    if tb == None or not count:
        return tb
    else:
        return skip_frames(tb.tb_next, count - 1)

def main():
    if len(sys.argv) == 1:
        repl()
    else:
        stdin = open(sys.argv[1])
        run_string(stdin.read())

if __name__ == '__main__':
    main()
