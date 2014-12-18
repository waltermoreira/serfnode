from base_handler import BaseHandler
from utils import truncated_stdout, with_payload, with_member_info


class MyHandler(BaseHandler):

    @truncated_stdout
    @with_payload
    def hello(self, who=None):
        """A custom user event."""

        print("Hello there, {}!".format(who))

    @with_payload
    def supervisor(self, **kwargs):
        """This event gets fired for change of state in supervisor."""

        print("Got a supervisor event with payload:")
        print(kwargs)

    @with_member_info
    def member_join(self, members):
        """This event gets fired on members joining.

        ``members`` is the dict with new members'

        """
        print("Hello to new members:")
        print(members)
