from mischief.actors.process_actor import ProcessActor
import utils
import serf


class EtcWriter(ProcessActor):

    def act(self):
        while True:
            self.receive(
                update_etc=self.write
            )

    def write(self, msg):
        etc = utils.read_etc_hosts()
        new = serf.serf_all_hosts()
        recent = serf.serf_recent_hosts(new)
        etc.update(recent)
        utils.write_etc_hosts(etc)
