dotlang
=======================

New language for Python VM.
It's a bit different - it's probably closest to stack-based languages.

Sample
---------------------

    > "hello world" print
    hello world
    > 1 2 add print
    3
    > "1 2" split map { int } sum
    3
