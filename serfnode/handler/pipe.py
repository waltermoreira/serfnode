import os
import select
import json


def server(pipe_file, handler):
    """A server for serf commands.

    Commands are a string object that are passed to serf.

    """
    try:
        os.unlink(pipe_file)
    except OSError:
        pass
    os.mkfifo(pipe_file)
    pipe = os.fdopen(
        os.open(pipe_file, os.O_RDONLY | os.O_NONBLOCK), 'r', 0)
    # open a dummy client to avoid getting EOF when other clients disconnect
    _pipe = os.fdopen(
        os.open(pipe_file, os.O_WRONLY | os.O_NONBLOCK), 'w', 0)
    polling = select.poll()
    polling.register(pipe.fileno())
    while True:
        polling.poll()
        cmd = pipe.readline()
        try:
            obj = json.loads(cmd)
        except:
            print("Wrong payload: {}".format(cmd))
            continue
        try:
            handler(obj)
        except:
            print("handler failed")

