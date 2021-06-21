#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage: $0 ptxfiles..."
    exit 1;
fi;

P=`dirname "$0"`
for PF in "$@"; do
    echo "=== $PF"
    O1=`mktemp`

    if $P/testparser.py "$PF" -n0 -o "$O1"; then
        O2=`mktemp`
        if $P/testparser.py "$O1" -n0 -o "$O2"; then
            if diff -u "$O1" "$O2"; then
                rm "$O1" "$O2"
                echo "OK:$PF"
            else
                echo "ERROR:$PF: Diff failed '$O1' '$O2'"
            fi;
        else
            echo "ERROR:$PF: Second-stage parsing failure (stage 1 output problem)"
        fi;
    else
        echo "ERROR:$PF: Parser failed"
    fi;
done;
