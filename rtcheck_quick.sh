#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage: $0 ptxfiles..."
    exit 1;
fi;

for PF in "$@"; do
echo "$PF"
O1=`mktemp`

if ./testparser.py "$PF" -n0 -o "$O1"; then
    O2=`mktemp`
    if ./testparser.py "$O1" -n0 -o "$O2"; then
        if diff -u "$O1" "$O2"; then
            rm "$O1"
            echo "OK"
        else
            echo "$O1" "$O2"
            #exit 1;
        fi;
    else
        echo "ERROR: Roundtrip parsing failure (stage 1 output problem)"
        #exit 1
    fi;
fi;
done;
