#!/usr/bin/env python
import os

from serf_master import SerfHandlerProxy
from base_handler import BaseHandler
try:
    from my_handler import MyHandler
except ImportError:
    MyHandler = BaseHandler


if __name__ == '__main__':
    handler = SerfHandlerProxy()
    role = os.environ.get('ROLE') or 'no_role'
    handler.register(role, MyHandler())
    handler.run()