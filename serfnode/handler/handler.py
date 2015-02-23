#!/usr/bin/env python
import os
import time
import multiprocessing

from serf_master import SerfHandlerProxy
from base_handler import BaseHandler
import config
try:
    from my_handler import MyHandler
except ImportError:
    MyHandler = BaseHandler


def async_post_registration_hook():
    p = multiprocessing.Process(target=post_registration_hook)
    p.start()


def post_registration_hook():
    while not os.path.exists('/agent_up'):
        time.sleep(0.1)
    MyHandler.init()


if __name__ == '__main__':
    handler = SerfHandlerProxy()
    role = config.role
    handler.register(role, MyHandler())
    async_post_registration_hook()
    handler.run()