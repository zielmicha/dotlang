import sys
import os
root = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__)) + '/..')
sys.path.append(root)

from dot.runtime import execute_file

for name in ['basic', 'dot_builtins']:
    execute_file('%s/tests/%s.dot' % (root, name))
