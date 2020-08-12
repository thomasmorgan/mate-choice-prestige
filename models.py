from dallinger.nodes import Source
from dallinger.networks import FullyConnected
from dallinger.models import Info
import json
import random
import glob


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
        """Assign fitness to property1."""
        self.property1 = repr(round)


class FaceSource(Source):

    __mapper_args__ = {"polymorphic_identity": "face_source"}

    def create_face_pairs(self):
        female_faces = glob.glob("./static/images/female_images/*.jpg")
        male_faces = glob.glob("./static/images/male_images/*.jpg")

        if self.network.role == "men":
            faces = male_faces
        elif self.network.role == "women":
            faces = female_faces
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
class Questionnaire(Source):
    """A Source that reads in a question from a file and transmits it."""

    __mapper_args__ = {"polymorphic_identity": "questionnaire_source"}

    def _contents(self):
        """Define the contents of new Infos.

        transmit() -> _what() -> create_information() -> _contents().
        """
        questions = [
            json.dumps({
                'question': 'What are piranhas?',
                'number': 1,
                'round': 0,
                'wrong_answer': 'Reptiles',
                'right_answer': 'Fish',
            }),
            json.dumps({
                'question': 'What is the currency used in Japan?',
                'number': 2,
                'round': 0,
                'wrong_answer': 'Dinar',
                'right_answer': 'Yen',
            }),
            json.dumps({
                'question': 'Which colors make green when mixed together?',
                'number': 3,
                'round': 0,
                'wrong_answer': 'Red and Blue',
                'right_answer': 'Blue and Yellow',
            }),
            json.dumps({
                'question': 'In what country is the Leaning Tower of Pisa located?',
                'number': 4,
                'round': 0,
                'wrong_answer': 'Spain',
                'right_answer': 'Italy',
            }),
            json.dumps({
                'question': 'What is the tallest animal in the world?',
                'number': 5,
                'round': 0,
                'wrong_answer': 'Elephant',
                'right_answer': 'Giraffe',
            }),
            json.dumps({
                'question': 'What is a xylophone?',
                'number': 6,
                'round': 0,
                'wrong_answer': 'A medical device',
                'right_answer': 'A musical instrument',
            }),
            json.dumps({
                'question': 'How many dots are on a six-sided die?',
                'number': 7,
                'round': 0,
                'wrong_answer': '19',
                'right_answer': '21',
            }),
            json.dumps({
                'question': 'Who wrote Hamlet?',
                'number': 8,
                'round': 0,
                'wrong_answer': 'Leonardo da Vinci',
                'right_answer': 'William Shakespeare',
            }),
            json.dumps({
                'question': 'What year did World War II end?',
                'number': 9,
                'round': 0,
                'wrong_answer': '1942',
                'right_answer': '1945',
            }),
            json.dumps({
                'question': 'Ottawa is the capital of which country?',
                'number': 10,
                'round': 0,
                'wrong_answer': 'Bolivia',
                'right_answer': 'Canada',
            }),
            json.dumps({
                'question': 'What do paleontologists study?',
                'number': 11,
                'round': 0,
                'wrong_answer': 'Ancient human civilizations',
                'right_answer': 'Dinosaur fossils',
            }),
            json.dumps({
                'question': 'What is a supernova?',
                'number': 12,
                'round': 0,
                'wrong_answer': 'An intense lightining storm',
                'right_answer': 'The explosion of a star',
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
                'question': 'Who invented the light bulb?',
                'number': 17,
                'round': 0,
                'wrong_answer': 'Alexander Graham Bell',
                'right_answer': 'Thomas Edison',
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
                'question': 'How many bones are in an elephant trunk?',
                'number': 20,
                'round': 0,
                'wrong_answer': '42',
                'right_answer': '0',
            }),
            json.dumps({
                'question': 'What is the longest river in the world?',
                'number': 21,
                'round': 0,
                'wrong_answer': 'Nile',
                'right_answer': 'Mississippi',
            }),
            json.dumps({
                'question': 'Which philosopher said, "I think, therefore I am"?',
                'number': 22,
                'round': 0,
                'wrong_answer': 'Friedrich Nietzsche',
                'right_answer': 'Rene Descartes',
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
                'question': 'What is the head of the Roman Catholic Church called?',
                'number': 25,
                'round': 0,
                'wrong_answer': 'Preacher',
                'right_answer': 'Pope',
            }),
            json.dumps({
                'question': 'Damascus is the capital of which country?',
                'number': 26,
                'round': 0,
                'wrong_answer': 'Lebanon',
                'right_answer': 'Syria',
            }),
            json.dumps({
                'question': 'What do plants need light for?',
                'number': 27,
                'round': 0,
                'wrong_answer': 'Respiration',
                'right_answer': 'Photosynthesis',
            }),
            json.dumps({
                'question': 'What do plants need light for?',
                'number': 27,
                'round': 0,
                'wrong_answer': 'Respiration',
                'right_answer': 'Photosynthesis',
            }),
            json.dumps({
                'question': 'Which word means "severe and intense"?',
                'number': 28,
                'round': 0,
                'wrong_answer': 'Chronic',
                'right_answer': 'Acute',
            }),
            json.dumps({
                'question': 'Which punctuation mark indicates a longer pause?',
                'number': 29,
                'round': 0,
                'wrong_answer': 'A comma',
                'right_answer': 'A semicolon',
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
