#!/usr/bin/env python

import functools
import os
import signal
import sys

import docker_utils


def handler(name, signum, frame):
    print('Should kill', name)
    try:
        docker_utils.client.remove_container(name, force=True)
    except Exception:
        pass
    sys.exit(0)


def launch(name, args):
    try:
        os.unlink('/app')
    except OSError:
        pass
    try:
        docker_utils.client.remove_container(name, force=True)
    except Exception:
        pass
    args.insert(0, '--cidfile=/app')
    docker_utils.docker('run', *args)


if __name__ == '__main__':
    name = sys.argv[1]
    args = sys.argv[2:]
    signal.signal(signal.SIGINT, functools.partial(handler, name))
    launch(name, args)
