from sys import stdin, argv

from dot.parse import parse
from dot.runtime import * # __main__ --> dot

if len(argv) == 2: stdin = open(argv[1])

code = parse(stdin.read())
RootFrame(Environ(parents=[builtins]), code).run()
