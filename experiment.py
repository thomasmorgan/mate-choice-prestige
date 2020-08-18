import logging
import gevent
import traceback
import math
import json

from dallinger.experiment import Experiment
from dallinger.nodes import Source
from dallinger.models import Node

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
        node = Node(network=network, participant=participant)
        node.details = {
            "score": 0,
            "id_within_group": network.size() - 2
        }
        return node

    def add_node_to_network(self, node, network):
        network.add_node(node)

        if (network.full):
            network.nodes(type=self.models.Questionnaire)[0].transmit()

        for n in network.nodes():
            if not isinstance(n, Source):
                n.receive()

    def info_post_request(self, node, info):
        if info.type == "quiz_answer":
            if info.contents == info.details["right_answer"]:
                details = node.details.copy()
                details["score"] = details["score"] + 1
                node.details = details

    @property
    def background_tasks(self):
        return [
            self.quiz_monitor,
            self.face_monitor
        ]

    def quiz_monitor(self):
        try:
            while any([net.round == 0 for net in self.networks()]):
                gevent.sleep(2)
                for net in [n for n in self.networks() if n.round == 0]:
                    question_source = net.nodes(type=self.models.Questionnaire)[0]
                    num_questions_sent = len(question_source.infos())
                    nodes = [n for n in net.nodes() if n.type == "node"]
                    num_questions_answered = [len(n.infos(type=self.models.QuizAnswer)) for n in nodes]

                    if num_questions_sent > 0 and all([n == num_questions_sent for n in num_questions_answered]):
                        if num_questions_sent == self.num_questions_in_round_0:
                            net.round = 1
                        else:
                            question_source.transmit()
                            for n in nodes:
                                n.receive()
                self.save()
            self.log("Beep boop. Quiz monitor shutting down.")
        except Exception:
            self.log(traceback.format_exc())

    def face_monitor(self):
        try:
            while any([net.round < 2 for net in self.networks()]):
                gevent.sleep(2)
                for net in [n for n in self.networks() if n.round == 1]:

                    # calculate how many FairPairs and Summaries have been sent
                    # and also how many FaceAnswer1s and FaceAnswer2s each node has made
                    face_source = net.nodes(type=self.models.FaceSource)[0]
                    num_faces_sent = len(face_source.infos(type=self.models.FacePairs))
                    num_summaries_sent = len(face_source.infos(type=self.models.Summary))
                    nodes = [n for n in net.nodes() if n.type == "node"]
                    num_faces_answered1 = [len(n.infos(type=self.models.FaceAnswer1)) for n in nodes]
                    num_faces_answered2 = [len(n.infos(type=self.models.FaceAnswer2)) for n in nodes]

                    self.log("******")
                    self.log("faces: {}. {}.".format(num_faces_sent, num_faces_answered1))
                    self.log("summaries: {}. {}.".format(num_summaries_sent, num_faces_answered2))

                    # we only need to do anything if all participants in this group have already responded to whatever they have been sent
                    if all([n == num_faces_sent for n in num_faces_answered1]) and all([n == num_summaries_sent for n in num_faces_answered2]):

                        # if fewer summaries have been sent than face pairs, send a summary
                        if num_summaries_sent < num_faces_sent:
                            self.log("Sending new summary!")
                            summary = self.get_answer_summary(net)
                            summary_info = self.models.Summary(origin=face_source, contents=json.dumps(summary))
                            face_source.transmit(what=summary_info)
                            for n in nodes:
                                n.receive()

                        # if the same number of summaries and face pairs have been sent, send a face pair
                        elif num_summaries_sent == num_faces_sent:
                            self.log("Sending new face pair!")
                            face_pair = self.models.FacePairs(contents=face_source._contents(), origin=face_source)
                            face_source.transmit(what=face_pair)
                            for n in nodes:
                                n.receive()

                self.save()
            self.log("Beep boop. Face monitor shutting down.")
        except Exception:
            self.log(traceback.format_exc())

    def get_answer_summary(self, network):
        # the goal of this function is to collate the answers of all participants in the network, and create a summary of them
        summary = []

        # to get the infos you need to do something like this:
        # first get all the nodes in the network
        # note the function now need to be passed 'network' as an argument
        nodes = [n for n in network.nodes() if n.type == "node"]

        # the get each nodes most recent answer (i.e. the FaceAnswer1 with the greatest id value)
        answers = [max(n.infos(type=self.models.FaceAnswer1), key=attrgetter("id")).contents for n in nodes]

        for node, answer in zip(nodes, answers):
            summary.append({
                "id": node.id,
                "id_within_group": node.details["id_within_group"],
                "score": node.details["score"],
                "face": answer
            })

        # you can print this above the return statement
        self.log(summary)

        # and you might want to return it.
        return summary

        # statements after a return statement will *never* run, return means stop execution of this function and go back to whatever called it.
