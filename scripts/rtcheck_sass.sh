#!/bin/bash

P=`dirname "$0"`

if [ $# -lt 1 ]; then
    echo "Usage: $0 ptxfiles..."
    exit 1;
fi;

# we use -O0 for an cheaper (and direct) translation
PTXOPT="-O0 -arch=sm_61"

for PF in "$@"; do
    echo "=== $PF"
    O1=`mktemp`
    OS1=`mktemp`

    if ptxas $PTXOPT "$PF" -o "$OS1"; then
        if $P/testparser.py "$PF" -n0 -o "$O1"; then
            OS2=`mktemp`
            if ptxas $PTXOPT "$O1" -o "$OS2"; then
                S1=`mktemp`
                S2=`mktemp`

                cuobjdump -sass "$OS1" > "$S1" || continue
                cuobjdump -sass "$OS2" > "$S2" || continue
                diff "$S1" "$S2" && echo "OK:$PF"
                rm "$O1" "$OS1" "$OS2" "$S1" "$S2"
            else
                echo "ERROR:$PF: ptxas failed on parsed output '$O1'"
            fi;
        else
            echo "ERROR:$PF: Parser failure"
        fi;
    else
        echo "ERROR:$PF: ptxas failed"
    fi;
done;
