#!/bin/bash
if [ "$(whoami)" = root ]; then
    ln -s $PWD/bin/dotlang /usr/local/bin
else
    ln -s $PWD/bin/dotlang ~/bin/
fi
