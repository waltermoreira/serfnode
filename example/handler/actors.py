import json

from mischief.actors.process_actor import ProcessActor


class ExampleActor(ProcessActor):

    def act(self):
        while True:
            self.receive(
                ping=self.ping
            )

    def ping(self, msg):
        """Receive a ping and save the message for posterity. """

        with open('/msg', 'w') as f:
            f.write(json.dumps(msg))
