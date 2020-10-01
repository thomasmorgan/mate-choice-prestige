from dallinger.nodes import Source
from dallinger.networks import FullyConnected
from dallinger.models import Info, Node

from datetime import datetime
from operator import attrgetter

import json
import random
import glob


class Player(Node):

    __mapper_args__ = {"polymorphic_identity": "player"}

    def __init__(self, network, participant=None):
        super().__init__(network, participant)
        other_ids = [n.details["id_within_group"] for n in network.nodes(type=Player) if n.id != self.id]
        if other_ids:
            my_id = [(r + 1) for r in range(network.max_size) if (r + 1) not in other_ids][0]
        else:
            my_id = 1

        self.details = {
            "score": 0,
            "id_within_group": my_id,
            "last_request": str(datetime.now())
        }

    @property
    def last_request(self):
        return datetime.strptime(self.details["last_request"], "%Y-%m-%d %H:%M:%S.%f")

    @last_request.setter
    def last_request(self, val):
        details = self.details.copy()
        details["last_request"] = str(val)
        self.details = details

    def update_last_request_time(self):
        if self.failed:
            raise ValueError("Cannot update last request for Player {} as it has failed.".format(self.id))
        self.last_request = datetime.now()

    def fail(self):
        super().fail()
        if self.network.infos():
            self.network.max_size -= 1
            self.network.calculate_full()


class QuizAnswer(Info):

    __mapper_args__ = {"polymorphic_identity": "quiz_answer"}


class FaceAnswer1(Info):

    __mapper_args__ = {"polymorphic_identity": "face_answer_1"}


class FaceAnswer2(Info):

    __mapper_args__ = {"polymorphic_identity": "face_answer_2"}


class FacePairs(Info):

    __mapper_args__ = {"polymorphic_identity": "face_pairs"}


class Summary(Info):

    __mapper_args__ = {"polymorphic_identity": "summary"}


class FaceNetwork(FullyConnected):

    __mapper_args__ = {"polymorphic_identity": "face_network"}

    @property
    def round(self):
        return int(self.property1)

    @round.setter
    def round(self, round):
        self.property1 = repr(round)

    @property
    def quiz_source(self):
        return self.nodes(type=Questionnaire)[0]

    @property
    def face_source(self):
        return self.nodes(type=FaceSource)[0]

    @property
    def players(self):
        return self.nodes(type=Player)

    def taking_too_long_to_fill(self, limit):
        players = self.nodes(type=Player)
        if not players:
            return False
        else:
            earliest_node = min(players, key=attrgetter('creation_time'))
            network_age = (datetime.now() - earliest_node.creation_time).total_seconds()
            return network_age > limit

    def shrink_to_current_size(self):
        self.max_size = self.size()
        self.calculate_full()

    def all_sent_quiz_questions_answered(self):
        num_questions_sent = len(self.quiz_source.infos())
        nodes = self.players
        num_questions_answered = [len(n.infos(type=QuizAnswer)) for n in nodes]

        return all([n_answered == num_questions_sent for n_answered in num_questions_answered])

    def ready_for_next_quiz_question(self):
        return self.full and self.all_sent_quiz_questions_answered()

    def send_next_quiz_question(self):
        self.quiz_source.transmit()
        for n in self.players:
            n.receive()

    def all_faces_and_summaries_answered(self):
        num_faces_sent = len(self.face_source.infos(type=FacePairs))
        num_summaries_sent = len(self.face_source.infos(type=Summary))

        nodes = self.players
        num_faces_answered1 = [len(n.infos(type=FaceAnswer1)) for n in nodes]
        num_faces_answered2 = [len(n.infos(type=FaceAnswer2)) for n in nodes]

        return all([n == num_faces_sent for n in num_faces_answered1]) and all([n == num_summaries_sent for n in num_faces_answered2])

    def send_next_face_pair_or_summary(self):
        if self.more_faces_than_summaries_sent():
            self.send_summary()
        else:
            self.send_face_pair()

    def more_faces_than_summaries_sent(self):
        num_faces_sent = len(self.infos(type=FacePairs))
        num_summaries_sent = len(self.infos(type=Summary))

        return num_faces_sent > num_summaries_sent

    def send_summary(self):
        self.face_source.transmit(what=Summary(
            origin=self.face_source,
            contents=self.get_answer_summary()
        ))

    def get_answer_summary(self):
        return json.dumps([{
            "id": node.id,
            "id_within_group": node.details["id_within_group"],
            "score": node.details["score"],
            "face": answer
        } for node, answer in zip(self.players, self.most_recent_face_choices())])

    def most_recent_face_choices(self):
        return [max(n.infos(type=FaceAnswer1), key=attrgetter("id")).contents for n in self.players]

    def send_face_pair(self):
        self.face_source.transmit()


class FaceSource(Source):

    __mapper_args__ = {"polymorphic_identity": "face_source"}

    def glob_images(self, sex):
        return glob.glob("./static/images/{}_images/*.jpg".format(sex))

    def create_face_pairs(self):
        if self.network.role == "men":
            faces = self.glob_images("male")
        elif self.network.role == "women":
            faces = self.glob_images("female")
        else:
            raise ValueError("Unknown network role: {}".format(self.network.role))

        random.shuffle(faces)

        face_pairs = []
        for i in range(int(len(faces) / 2)):
            pair = json.dumps({
                'number': i + 1,
                'face1': faces[i * 2],
                'face2': faces[i * 2 + 1],
                'round': 1,
                'question': 'Which of these individuals would you prefer as a romantic partner?'
            })
            face_pairs.append(pair)

        self.property1 = json.dumps(face_pairs)

    @property
    def face_pairs(self):
        return json.loads(self.property1)

    def _contents(self):
        number_transmissions = len(self.infos(type=FacePairs))
        if number_transmissions < len(self.face_pairs):
            question = self.face_pairs[number_transmissions]
        else:
            question = self.face_pairs[-1]
        return question

    def _info_type(self):
        return FacePairs


class Questionnaire(Source):

    __mapper_args__ = {"polymorphic_identity": "questionnaire_source"}

    def _contents(self):
        questions = [
            json.dumps({
                'question': 'Which is a liquid at room tempurature?',
                'number': 1,
                'round': 0,
                'wrong_answer': 'Magnesium',
                'right_answer': 'Mercury',
            }),
            json.dumps({
                'question': 'Which Olympian has won the most gold medals?',
                'number': 2,
                'round': 0,
                'wrong_answer': 'Usain Bolt',
                'right_answer': 'Michael Phelps',
            }),
            json.dumps({
                'question': 'Who invented the cotton gin?',
                'number': 3,
                'round': 0,
                'wrong_answer': 'Thomas Edison',
                'right_answer': 'Eli Whitney',
            }),
            json.dumps({
                'question': 'What lake has the greatest surface area in the world?',
                'number': 4,
                'round': 0,
                'wrong_answer': 'Lake Tahoe',
                'right_answer': 'Caspian Sea',
            }),
            json.dumps({
                'question': 'Who challenged Beethoven to an improvisation contest and suffered an embarrassing loss?',
                'number': 5,
                'round': 0,
                'wrong_answer': 'Antonio Salieri',
                'right_answer': 'Daniel Steibelt',
            }),
            json.dumps({
                'question': 'Which is the largest living organism in the world?',
                'number': 6,
                'round': 0,
                'wrong_answer': 'The Blue Whale',
                'right_answer': 'The Humongous Fungus',
            }),
            json.dumps({
                'question': 'How many dots are on a six-sided die?',
                'number': 7,
                'round': 0,
                'wrong_answer': '19',
                'right_answer': '21',
            }),
            json.dumps({
                'question': 'Which country is landlocked completely by another nation?',
                'number': 8,
                'round': 0,
                'wrong_answer': 'Nepal',
                'right_answer': 'Lesotho',
            }),
            json.dumps({
                'question': 'What year did World War II end?',
                'number': 9,
                'round': 0,
                'wrong_answer': '1942',
                'right_answer': '1945',
            }),
            json.dumps({
                'question': 'What American president is also in the Wrestling Hall of Fame?',
                'number': 10,
                'round': 0,
                'wrong_answer': 'William Howard Taft',
                'right_answer': 'Abraham Lincoln',
            }),
            json.dumps({
                'question': 'What do paleontologists study?',
                'number': 11,
                'round': 0,
                'wrong_answer': 'Ancient human civilizations',
                'right_answer': 'Dinosaur fossils',
            }),
            json.dumps({
                'question': 'Taumata, the nickname of the place with the longest name in the world, is located in which country?',
                'number': 12,
                'round': 0,
                'wrong_answer': 'Indonesia',
                'right_answer': 'New Zealand',
            }),
            json.dumps({
                'question': 'How can bats fly in the dark?',
                'number': 13,
                'round': 0,
                'wrong_answer': 'X-ray vision',
                'right_answer': 'Echolocation',
            }),
            json.dumps({
                'question': 'What is the technical term for a lie detector test?',
                'number': 14,
                'round': 0,
                'wrong_answer': 'Seismograph',
                'right_answer': 'Polygraph',
            }),
            json.dumps({
                'question': 'What is an echidna?',
                'number': 15,
                'round': 0,
                'wrong_answer': 'A Spanish dessert',
                'right_answer': 'An Australian mammal',
            }),
            json.dumps({
                'question': 'What is the smallest country in the world?',
                'number': 16,
                'round': 0,
                'wrong_answer': 'Monaco',
                'right_answer': 'Vatican City',
            }),
            json.dumps({
                'question': 'Which country has the longest coastline?',
                'number': 17,
                'round': 0,
                'wrong_answer': 'Australia',
                'right_answer': 'Canada',
            }),
            json.dumps({
                'question': 'In Greek mythology, who is the Goddess of Agriculture?',
                'number': 18,
                'round': 0,
                'wrong_answer': 'Persephone',
                'right_answer': 'Demeter',
            }),
            json.dumps({
                'question': 'What is Xylography?',
                'number': 19,
                'round': 0,
                'wrong_answer': 'The study of hieroglyphs',
                'right_answer': 'The art of making wood engravings',
            }),
            json.dumps({
                'question': 'Who is the youngest player to ever be inducted into the Pro Football Hall of Fame?',
                'number': 20,
                'round': 0,
                'wrong_answer': 'Jim Brown',
                'right_answer': 'Gale Sayers',
            }),
            json.dumps({
                'question': 'What is the longest river in the world?',
                'number': 21,
                'round': 0,
                'wrong_answer': 'Nile',
                'right_answer': 'Mississippi',
            }),
            json.dumps({
                'question': 'Which European explorer was the first foreigner to discover America?',
                'number': 22,
                'round': 0,
                'wrong_answer': 'Christopher Columbus',
                'right_answer': 'Leif Erikson',
            }),
            json.dumps({
                'question': 'What is the chemical symbol for potassium?',
                'number': 23,
                'round': 0,
                'wrong_answer': 'P',
                'right_answer': 'K',
            }),
            json.dumps({
                'question': 'What does a mycologist study?',
                'number': 24,
                'round': 0,
                'wrong_answer': 'Mushrooms',
                'right_answer': 'Anti-matter',
            }),
            json.dumps({
                'question': 'When the first dollar bill was issued, whose face was printed on the front?',
                'number': 25,
                'round': 0,
                'wrong_answer': 'William McKinley',
                'right_answer': 'Salmon P. Chase',
            }),
            json.dumps({
                'question': 'Damascus is the capital of which country?',
                'number': 26,
                'round': 0,
                'wrong_answer': 'Lebanon',
                'right_answer': 'Syria',
            }),
            json.dumps({
                'question': 'Which human disorder makes it difficult for a person to recognize faces?',
                'number': 27,
                'round': 0,
                'wrong_answer': 'Derealization disorder',
                'right_answer': 'Prosopagnosia',
            }),
            json.dumps({
                'question': 'What was the pen name of author Charlotte Brontë?',
                'number': 28,
                'round': 0,
                'wrong_answer': 'Jane Eyre',
                'right_answer': 'Currer Bell',
            }),
            json.dumps({
                'question': 'Which of the following popular condiments was once sold as a cure for indigestion?',
                'number': 29,
                'round': 0,
                'wrong_answer': 'Tartar sauce',
                'right_answer': 'Ketchup',
            }),
            json.dumps({
                'question': 'How many different colors are on the flag of South Africa?',
                'number': 30,
                'round': 0,
                'wrong_answer': '9',
                'right_answer': '6',
            }),
        ]

        number_transmissions = len(self.infos())
        if number_transmissions < len(questions):
            question = questions[number_transmissions]
        else:
            question = questions[-1]
        return question
