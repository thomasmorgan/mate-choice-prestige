from dallinger.nodes import Source
import json
import random
import glob


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
                'question': 'Which of these faces is best?'
            })
            face_pairs.append(pair)

        self.property1 = json.dumps(face_pairs)

    @property
    def face_pairs(self):
        return json.loads(self.property1)

    def _contents(self):
        number_transmissions = len(self.infos())
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
                'topic': 'Practice',###Can we chagne the name of this to pretest? or is pracice called somewhere else?
                'wrong_answer': 'Reptiles',
                'right_answer': 'Fish',
                'pic': False,### Do we want photos to be assocaiated with the pretest questions?
            }),
            json.dumps({
                'question': 'What is the currency used in Japan?',
                'number': 2,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Dinar',
                'right_answer': 'Yen',
                'pic': False,
            }),
            json.dumps({
                'question': 'Which colors make green when mixed together?',
                'number': 3,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Red and Blue',
                'right_answer': 'Blue and Yellow',
                'pic': False,
            }),
            json.dumps({
                'question': 'In what country is the Leaning Tower of Pisa located?',
                'number': 4,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Spain',
                'right_answer': 'Italy',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is the tallest animal in the world?',
                'number': 5,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Elephant',
                'right_answer': 'Giraffe',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is a xylophone?',
                'number': 6,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'A medical device',
                'right_answer': 'A musical instrument',
                'pic': False,
            }),
            json.dumps({
                'question': 'How many dots are on a six-sided die?',
                'number': 7,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': '19',
                'right_answer': '21',
                'pic': False,
            }),
            json.dumps({
                'question': 'Who wrote Hamlet?',
                'number': 8,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Leonardo da Vinci',
                'right_answer': 'William Shakespeare',
                'pic': False,
            }),
            json.dumps({
                'question': 'What year did World War II end?',
                'number': 9,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': '1942',
                'right_answer': '1945',
                'pic': False,
            }),
            json.dumps({
                'question': 'Ottawa is the capital of which country?',
                'number': 10,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Bolivia',
                'right_answer': 'Canada',
                'pic': False,
            }),
            json.dumps({
                'question': 'What do paleontologists study?',
                'number': 11,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Ancient human civilizations',
                'right_answer': 'Dinosaur fossils',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is a supernova?',
                'number': 12,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'An intense lightining storm',
                'right_answer': 'The explosion of a star',
                'pic': False,
            }),
            json.dumps({
                'question': 'How can bats fly in the dark?',
                'number': 13,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'X-ray vision',
                'right_answer': 'Echolocation',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is the technical term for a lie detector test?',
                'number': 14,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Seismograph',
                'right_answer': 'Polygraph',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is an echidna?',
                'number': 15,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'A Spanish dessert',
                'right_answer': 'An Australian mammal',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is the smallest country in the world?',
                'number': 16,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Monaco',
                'right_answer': 'Vatican City',
                'pic': False,
            }),
            json.dumps({
                'question': 'Who invented the light bulb?',
                'number': 17,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Alexander Graham Bell',
                'right_answer': 'Thomas Edison',
                'pic': False,
            }),
            json.dumps({
                'question': 'In Greek mythology, who is the Goddess of Agriculture?',
                'number': 18,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Persephone',
                'right_answer': 'Demeter',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is Xylography?',
                'number': 19,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'The study of hieroglyphs',
                'right_answer': 'The art of making wood engravings',
                'pic': False,
            }),
            json.dumps({
                'question': 'How many bones are in an elephant trunk?',
                'number': 20,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': '42',
                'right_answer': '0',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is the longest river in the world?',
                'number': 21,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Nile',
                'right_answer': 'Mississippi',
                'pic': False,
            }),
            json.dumps({
                'question': 'Which philosopher said, "I think, therefore I am"?',
                'number': 22,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Friedrich Nietzsche',
                'right_answer': 'Rene Descartes',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is the chemical symbol for potassium?',
                'number': 23,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'P',
                'right_answer': 'K',
                'pic': False,
            }),
            json.dumps({
                'question': 'What does a mycologist study?',
                'number': 24,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Mushrooms',
                'right_answer': 'Anti-matter',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is the head of the Roman Catholic Church called?',
                'number': 25,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Preacher',
                'right_answer': 'Pope',
                'pic': False,
            }),
            json.dumps({
                'question': 'Damascus is the capital of which country?',
                'number': 26,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Lebanon',
                'right_answer': 'Syria',
                'pic': False,
            }),
            json.dumps({
                'question': 'What do plants need light for?',
                'number': 27,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Respiration',
                'right_answer': 'Photosynthesis',
                'pic': False,
            }),
            json.dumps({
                'question': 'What do plants need light for?',
                'number': 27,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Respiration',
                'right_answer': 'Photosynthesis',
                'pic': False,
            }),
            json.dumps({
                'question': 'Which word means "severe and intense"?',
                'number': 28,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'Chronic',
                'right_answer': 'Acute',
                'pic': False,
            }),
            json.dumps({
                'question': 'Which punctuation mark indicates a longer pause?',
                'number': 29,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': 'A comma',
                'right_answer': 'A semicolon',
                'pic': False,
            }),
            json.dumps({
                'question': 'How many different colors are on the flag of South Africa?',
                'number': 30,
                'round': 0,
                'topic': 'Practice',
                'wrong_answer': '9',
                'right_answer': '6',
                'pic': False,
            }),
        ]

        number_transmissions = len(self.infos())
        if number_transmissions < len(questions):
            question = questions[number_transmissions]
        else:
            question = questions[-1]
        return question
