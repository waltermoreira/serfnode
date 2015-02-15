#!/usr/bin/env python
from serf_master import SerfHandlerProxy
from base_handler import BaseHandler
import config
try:
    from my_handler import MyHandler
except ImportError:
    MyHandler = BaseHandler


if __name__ == '__main__':
    handler = SerfHandlerProxy()
    role = config.role
    handler.register(role, MyHandler())
    handler.run()