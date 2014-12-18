from base_handler import BaseHandler
from utils import truncated_stdout, with_payload


class MyHandler(BaseHandler):

    @truncated_stdout
    @with_payload
    def hello(self, who=None):
        print("Hello there, {}!".format(who))
