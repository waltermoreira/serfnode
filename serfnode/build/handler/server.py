from contextlib import contextmanager
import threading
import traceback

import zmq
from logbook import Logger


Context = zmq.Context()
logger = Logger('minion server')


@contextmanager
def zmq_socket(zmq_type):
    """Context manager for zmq sockets.

    Use as::

        with zmq_socket(zmq.REP) as s:
            ...

    """
    s = Context.socket(zmq_type)
    yield s
    s.close()


class Server(object):
    """A generic REQ/REP server."""

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.setup()

    def setup(self):
        pass

    def handle(self, data):
        raise NotImplementedError

    @property
    def name(self):
        return '{}-{}:{}'.format(type(self).__name__,
                                 self.ip,
                                 self.port)

    def start(self):
        self.thread = threading.Thread(target=self._server,
                                       args=(logger,))
        self.thread.name = self.name
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        with zmq_socket(zmq.REQ) as s:
            ip = self.ip if self.ip != '*' else 'localhost'
            s.connect('tcp://{}:{}'.format(ip, self.port))
            s.send_json({'__quit__': True})
            s.recv_json()
            self.thread.join()

    def _server(self, logger):
        with zmq_socket(zmq.REP) as s:
            s.bind('tcp://{}:{}'.format(self.ip, self.port))
            while True:
                data = s.recv_json()
                resp = None
                try:
                    if data.get('__quit__'):
                        logger.debug('asked to shutdown')
                        return
                    resp = self.handle(data)
                except Exception:
                    exc = traceback.format_exc()
                    logger.debug('got an exception:')
                    logger.debug(exc)
                    resp = {'exception': exc}
                finally:
                    s.send_json(resp)
