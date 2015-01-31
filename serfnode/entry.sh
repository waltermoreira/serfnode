#!/bin/bash

if [[ "$#" -gt 0 ]]; then
    /deploy/deploy.py $*
else
    exec /handler/entry.sh
fi

