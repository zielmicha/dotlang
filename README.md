dotlang
=======================

New language for Python VM.
It's a bit different - it's probably closest to stack-based languages.

Sample
---------------------

    $ bin/dotlang
    > "hello world"
    hello world
    > 1 2 add
    3
    > "1 2" split map { int } sum
    3
    > 1 2 list map { 4 add }
    [5, 6]
