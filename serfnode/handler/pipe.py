from __future__ import print_function

import os
import select
import json
import sys


def server(pipe_file, handler):
    """A server for serf commands.

    Commands are a string object that are passed to serf.

    """
    os.mkfifo(pipe_file)
    pipe = os.fdopen(
        os.open(pipe_file, os.O_RDONLY | os.O_NONBLOCK), 'r', 0)
    # open a dummy client to avoid getting EOF when other clients disconnect
    _pipe = os.fdopen(
        os.open(pipe_file, os.O_WRONLY | os.O_NONBLOCK), 'w', 0)
    polling = select.poll()
    polling.register(pipe.fileno(), select.POLLIN)
    while True:
        result = polling.poll()
        if not result:
            continue
        try:
            cmd = pipe.readline()
        except:
            print('Could not read from pipe', file=sys.stderr)
            continue
        try:
            obj = json.loads(cmd)
        except:
            print("Wrong payload: {}".format(cmd), file=sys.stderr)
            continue
        try:
            handler(obj)
        except:
            print("handler failed", file=sys.stderr)

