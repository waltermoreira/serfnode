#!/bin/bash

if [[ "$#" -gt 0 ]]; then
    exec /deploy/deploy.py $*
else
    exec /handler/entry.sh
fi

