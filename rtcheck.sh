#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage: $0 ptxfile"
    exit 1;
fi;

O1=`mktemp`

if ./testparser.py "$1" -n0 -o "$O1"; then
    O2=`mktemp`
    if ./testparser.py "$O1" -n0 -o "$O2"; then
        if diff -u "$O1" "$O2"; then
            rm "$O1"
            if ptxas -arch=sm_75 "$O2"; then
                rm "$O2"
                echo "OK"
                exit 0;
            else
                echo "ptxas failed on '$O2'"
                exit 1;
            fi;
        else
            echo "$O1" "$O2"
            exit 1;
        fi;
    fi;
fi;
