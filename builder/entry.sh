#!/bin/bash

cat /proc/mounts | awk '{print $2}' | grep '/target' > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Please, mount the destination directory in '/target'"
    echo 'For example: docker run -it -v $(pwd):/target serfnode_init init'
    exit 1
fi

if [ "$1" == "init" ]; then
    cookiecutter /template
else
    # just update roles
    (
        cd /tmp;
        cookiecutter --no-input /roles_template;
    )
    rm -rf deploy/roles
    cp -r /tmp/my_serfnode/deploy/roles deploy/
fi
