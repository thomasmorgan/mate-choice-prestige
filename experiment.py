"""Bartlett's transmission chain experiment from Remembering (1932)."""

import logging
import gevent
import traceback

from dallinger.config import get_config
from dallinger.networks import FullyConnected
from dallinger.experiment import Experiment
from dallinger.nodes import Source

logger = logging.getLogger(__file__)


def extra_parameters():
    config = get_config()
    config.register("num_participants", int)


class Bartlett1932(Experiment):
    """Define the structure of the experiment."""

    def __init__(self, session=None):
        """Call the same function in the super (see experiments.py in dallinger).

        A few properties are then overwritten.

        Finally, setup() is called.
        """
        super(Bartlett1932, self).__init__(session)
        from . import models  # Import at runtime to avoid SQLAlchemy warnings

        self.models = models
        self.experiment_repeats = 1
        self.initial_recruitment_size = self.num_participants
        if session:
            self.setup()

    def configure(self):
        config = get_config()
        self.num_participants = config.get("num_participants")

    def setup(self):
        """Setup the networks.

        Setup only does stuff if there are no networks, this is so it only
        runs once at the start of the experiment. It first calls the same
        function in the super (see experiments.py in dallinger). Then it adds a
        source to each network.
        """
        if not self.networks():
            super(Bartlett1932, self).setup()
            for net in self.networks():
                self.models.Questionnaire(network=net)

    def create_network(self):
        """Return a new network."""
        return FullyConnected(max_size=self.num_participants + 1)

    def add_node_to_network(self, node, network):
        """Add node to the chain and receive transmissions."""
        network.add_node(node)

        if (network.full):
            source = network.nodes(type=Source)[0]
            source.transmit()

        for n in network.nodes():
            if not isinstance(n, Source):
                n.receive()

    def recruit(self):
        """Recruit one participant at a time until all networks are full."""
        if self.networks(full=False):
            self.recruiter.recruit(n=1)
        else:
            self.recruiter.close_recruitment()

    @property
    def background_tasks(self):
        return [
            self.quiz_monitor,
        ]

    def quiz_monitor(self):
        try:
            quiz_ongoing = True
            while quiz_ongoing:
                gevent.sleep(2)
                for net in self.networks():
                    source = net.nodes(type=self.models.Questionnaire)[0]
                    num_questions_sent = len(source.infos())
                    nodes = [n for n in net.nodes() if n.type != "questionnaire_source"]
                    num_questions_answered = [len(n.infos()) for n in nodes]

                    ready_for_next_question = num_questions_sent > 0 and all([n == num_questions_sent for n in num_questions_answered])
                    if ready_for_next_question:
                        source.transmit()
                        for n in nodes:
                            n.receive()
                        self.save()
        except Exception:
            self.log(traceback.format_exc())
