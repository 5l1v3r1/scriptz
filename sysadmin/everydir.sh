#!/bin/bash
#Description: run a command in every subdirectory of CWD
#Usage: everydir [command]
subdirs=$(find "$PWD" -maxdepth 1 -type d)
for i in $subdirs
    do cd "$i"
    "$@"
done
