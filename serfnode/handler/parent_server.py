#!/usr/bin/env python

import os
import select
import json

import serf


def server():
    """A server for serf commands.

    Commands are a string object that are passed to serf.

    """
    os.mkfifo('/serfnode/parent')
    pipe = os.fdopen(
        os.open('/serfnode/parent', os.O_RDONLY | os.O_NONBLOCK), 'r', 0)
    # open a dummy client to avoid getting EOF when other clients disconnect
    _pipe = os.fdopen(
        os.open('/serfnode/parent', os.O_WRONLY | os.O_NONBLOCK), 'w', 0)
    polling = select.poll()
    polling.register(pipe.fileno())
    while True:
        polling.poll()
        cmd = pipe.readline()
        try:
            name, payload = json.loads(cmd)
        except:
            print("Wrong payload: {}".format(cmd))
        try:
            serf.serf_plain('event', name, json.dumps(payload))
        except:
            print("serf command failed")


if __name__ == '__main__':
    server()
