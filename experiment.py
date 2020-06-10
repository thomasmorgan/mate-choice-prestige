"""Bartlett's transmission chain experiment from Remembering (1932)."""

import logging
import gevent
import traceback
import math

from dallinger.networks import FullyConnected
from dallinger.experiment import Experiment
from dallinger.nodes import Source
from dallinger.models import Node

from operator import attrgetter

logger = logging.getLogger(__file__)


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
        self.ppts_per_network = 2
        self.over_recruitment_factor = 0
        self.initial_recruitment_size = math.ceil(self.experiment_repeats * self.ppts_per_network * (1 + self.over_recruitment_factor))
        self.num_questions_in_round_0 = 5
        if session:
            self.setup()

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
                if net.id % 2 == 0:
                    net.role = "men"
                else:
                    net.role = "women"
                self.models.Questionnaire(network=net)
                face_source = self.models.FaceSource(network=net)
                face_source.create_face_pairs()

    def create_network(self):
        """Return a new network."""
        return FullyConnected(max_size=self.ppts_per_network + 2)

    def get_network_for_participant(self, participant):
        # get participants preference
        preference = participant.questions()[0].response
        self.log("Preference is {}".format(preference))

        # if its men or women:
        if preference in ["men", "women"]:

            # get all networks for that preference that are not yet full
            available_networks = self.networks(role=preference, full=False)
            self.log("Available networks are {}".format([str(n) for n in available_networks]))

            # put them in the one with the lowest id
            if available_networks:
                first_network = min(available_networks, key=attrgetter('id'))
                self.log("Putting participant in {}".format(first_network))
                return first_network

            # if there are not networks with space for their preference
            else:

                self.log("No networks available, checking for convertable network")
                # look for any networks for the opposite preference, but that are currently totally empty
                opposite_preference = [p for p in ["men", "women"] if p != preference][0]
                opposite_networks = self.networks(role=opposite_preference)
                empty_networks = [net for net in opposite_networks if net.size() == 2]
                self.log("Convertable networks: {}".format([str(n) for n in empty_networks]))

            #   if one exists convert it to their preference, add them to it
                if empty_networks:
                    chosen_network = max(empty_networks, key=attrgetter('id'))
                    self.log("Converting: {}".format(chosen_network))
                    chosen_network.role = preference
                    return chosen_network

            #   else return None
                else:
                    self.log("No convertable networks available either, returning None")
                    return None

        # else if its both
        else:
            # get the earliest network for men and women, put them in the bigger of the two
            self.log("Looking for any available networks")
            available_networks = self.networks(full=False)
            sizes = [n.size() for n in available_networks]
            max_size = max(sizes)
            biggest_network = min([n for n in available_networks if n.size() == max_size], key=attrgetter('id'))
            self.log("Returning biggest network, {} with size {}".format(biggest_network, max_size))
            return biggest_network

    def create_node(self, participant, network):
        node = Node(network=network, participant=participant)
        node.details = {"score": 0}
        return node

    def add_node_to_network(self, node, network):
        """Add node to the chain and receive transmissions."""
        network.add_node(node)

        if (network.full):
            source = network.nodes(type=self.models.Questionnaire)[0]
            source.transmit()

        for n in network.nodes():
            if not isinstance(n, Source):
                n.receive()

    def info_post_request(self, node, info):
        if info.details["round"] == 0 and info.contents == info.details["right_answer"]:
            details = node.details.copy()
            details["score"] = details["score"] + 1
            node.details = details

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
            round_0 = True
            quiz_ongoing = True
            while quiz_ongoing:
                gevent.sleep(2)
                for net in self.networks():
                    question_source = net.nodes(type=self.models.Questionnaire)[0]
                    face_source = net.nodes(type=self.models.FaceSource)[0]
                    num_questions_sent = len(question_source.infos()) + len(face_source.infos())

                    nodes = [n for n in net.nodes() if n.type == "node"]
                    num_questions_answered = [len(n.infos()) for n in nodes]

                    ready_for_next_question = num_questions_sent > 0 and all([n == num_questions_sent for n in num_questions_answered])
                    if ready_for_next_question:
                        if round_0:
                            source = question_source
                        else:
                            source = face_source
                        source.transmit()
                        for n in nodes:
                            n.receive()
                        if (num_questions_sent + 1 == self.num_questions_in_round_0):
                            round_0 = False
                        self.save()
        except Exception:
            self.log(traceback.format_exc())
