#!/bin/bash

if [[ "$1" == "/alias" ]]; then
    /alias;
    exit 1;
fi;
if [[ "$#" -gt 0 ]]; then
    /deploy/deploy.py $*
else
    exec /handler/entry.sh
fi

