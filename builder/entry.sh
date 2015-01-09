#!/bin/bash

cat /proc/mounts | awk '{print $2}' | grep '/target' > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Please, mount the destination directory in '/target'"
    echo 'For example: docker run -it -v $(pwd):/target serfnode_init'
    exit 1
fi

cookiecutter /template
