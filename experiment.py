import logging
import gevent
import traceback
import math

from dallinger.experiment import Experiment

from operator import attrgetter

logger = logging.getLogger(__file__)


class MateChoicePrestige(Experiment):

    def __init__(self, session=None):
        super().__init__(session)
        from . import models
        self.models = models

        self.experiment_repeats = 1
        self.ppts_per_network = 2
        self.over_recruitment_factor = 0
        self.initial_recruitment_size = math.ceil(self.experiment_repeats * self.ppts_per_network * (1 + self.over_recruitment_factor))
        self.num_questions_in_round_0 = 5
        self.num_questions_in_round_1 = 5
        self.inactivity_time_limit = 20

        self.known_classes["QuizAnswer"] = self.models.QuizAnswer
        self.known_classes["FaceAnswer1"] = self.models.FaceAnswer1
        self.known_classes["FaceAnswer2"] = self.models.FaceAnswer2
        self.known_classes["FacePairs"] = self.models.FacePairs
        self.known_classes["Summary"] = self.models.Summary

        if session:
            self.setup()

    def setup(self):
        if not self.networks():
            super().setup()
            for net in self.networks():
                if net.id % 2 == 0:
                    net.role = "men"
                else:
                    net.role = "women"
                self.models.Questionnaire(network=net)
                face_source = self.models.FaceSource(network=net)
                face_source.create_face_pairs()

    def create_network(self):
        net = self.models.FaceNetwork(max_size=self.ppts_per_network + 2)
        net.round = 0
        return net

    def get_network_for_participant(self, participant):
        preference = participant.questions()[0].response

        if preference == "both":
            return self.fullest_available_network()

        elif preference in ["men", "women"]:
            available_networks = self.networks(role=preference, full=False)

            if available_networks:
                return min(available_networks, key=attrgetter('id'))

            else:
                opposite_preference = "men" if preference == "women" else "women"
                opposite_networks = self.networks(role=opposite_preference)
                convertable_networks = [net for net in opposite_networks if net.size() == 2]
                if convertable_networks:
                    chosen_network = max(convertable_networks, key=attrgetter('id'))
                    chosen_network.role = preference
                    face_source = chosen_network.nodes(type=self.models.FaceSource)[0]
                    face_source.create_face_pairs()
                    return chosen_network
        return None

    def fullest_available_network(self):
        available_networks = self.networks(full=False)
        if not available_networks:
            return None
        sizes = [n.size() for n in available_networks]
        max_size = max(sizes)
        return min([n for n in available_networks if n.size() == max_size], key=attrgetter('id'))

    def create_node(self, participant, network):
        node = self.models.Player(network=network, participant=participant)
        return node

    def add_node_to_network(self, node, network):
        network.add_node(node)
        if (network.full):
            network.quiz_source.transmit()
            for n in network.players:
                n.receive()

    def info_post_request(self, node, info):
        node.update_last_request_time()
        if info.type == "quiz_answer":
            if info.contents == info.details["right_answer"]:
                details = node.details.copy()
                details["score"] = details["score"] + 1
                node.details = details

    def info_get_request(self, node, infos):
        node.update_last_request_time()

    def node_get_request(self, node, nodes):
        node.update_last_request_time()

    @property
    def background_tasks(self):
        return [
            self.quiz_monitor,
            self.face_monitor,
            self.activity_monitor
        ]

    def quiz_monitor(self):
        try:
            while self.quiz_ongoing():
                gevent.sleep(2)
                self.advance_quiz()
                self.save()
            self.log("Beep boop. Quiz monitor shutting down.")
        except Exception:
            self.log(traceback.format_exc())

    def advance_quiz(self):
        for net in self.networks_in_quiz():
            if self.quiz_completed(net):
                net.round = 1
            elif net.ready_for_next_quiz_question():
                net.send_next_quiz_question()

    def quiz_ongoing(self):
        return any([net.round == 0 for net in self.networks()])

    def networks_in_quiz(self):
        return [n for n in self.networks() if n.round == 0]

    def quiz_completed(self, net):
        all_quiz_questions_sent = len(net.quiz_source.infos()) == self.num_questions_in_round_0
        return all_quiz_questions_sent and net.all_sent_quiz_questions_answered()

    def face_monitor(self):
        try:
            while self.experiment_ongoing():
                gevent.sleep(2)
                self.advance_faces()
                self.save()
            self.log("Beep boop. Face monitor shutting down.")
        except Exception:
            self.log(traceback.format_exc())

    def experiment_ongoing(self):
        return any([net.round < 2 for net in self.networks()])

    def advance_faces(self):
        for net in self.networks_in_faces():
            if self.faces_completed(net):
                net.round = 2
            elif net.all_faces_and_summaries_answered():
                net.send_next_face_pair_or_summary()
                for n in net.players:
                    n.receive()

    def networks_in_faces(self):
        return [n for n in self.networks() if n.round == 1]

    def faces_completed(self, net):
        all_face_pairs_sent = len(net.face_source.infos(type=self.models.FacePairs)) == self.num_questions_in_round_1
        all_summaries_sent = len(net.face_source.infos(type=self.models.Summary)) == self.num_questions_in_round_1
        return all_face_pairs_sent and all_summaries_sent and net.all_faces_and_summaries_answered()

    def activity_monitor(self):
        try:
            while self.experiment_ongoing():
                gevent.sleep(2)
                self.find_and_remove_frozen_players()
                self.save()
            self.log("Beep boop. Activity monitor shutting down.")
        except Exception:
            self.log(traceback.format_exc())

    def find_and_remove_frozen_players(self):
        for net in self.started_yet_unfinished_networks():
            most_recent_activity = max([p.last_request for p in net.players])
            for p in net.players:
                if (most_recent_activity - p.last_request).total_seconds() > self.inactivity_time_limit:
                    p.fail()

    def started_yet_unfinished_networks(self):
        return [n for n in self.networks() if n.players and n.round < 2]
