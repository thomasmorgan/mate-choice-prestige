from dallinger.nodes import Source
import json
import random


class FaceSource(Source):

    __mapper_args__ = {"polymorphic_identity": "face_source"}

    def contents(self):
        female_faces = [124, 125, 126, 128]
        male_faces = [1, 10, 109, 147]

        if self.network.role == "men":
            faces = ['male_images/' + str(i) + "-12.jpg" for i in male_faces]
        elif self.network.role == "women":
            faces = ['female_images/' + str(i) + "-12.jpg" for i in female_faces]
        else:
            raise ValueError("Unknown network role: {}".format(self.network.role))

        random.shuffle(faces)

        face_pairs = []
        for i in range(len(faces) / 2):
            pair = json.dumps({
                'pair': i,
                'face1': faces[i * 2],
                'face2': faces[i * 2 + 1]
            })
            face_pairs.append(pair)

        number_transmissions = len(self.infos())
        if number_transmissions < len(face_pairs):
            question = face_pairs[number_transmissions]
        else:
            question = face_pairs[-1]
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
                'Wwer': 'Reptiles',
                'Rwer': 'Fish',
                'pic': False,### Do we want photos to be assocaiated with the pretest questions?
            }),
            json.dumps({
                'question': 'What is the currency used in Japan?',
                'number': 2,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Dinar',
                'Rwer': 'Yen',
                'pic': False,
            }),
            json.dumps({
                'question': 'Which colors make green when mixed together?',
                'number': 3,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Red and Blue',
                'Rwer': 'Blue and Yellow',
                'pic': False,
            }),
            json.dumps({
                'question': 'In what country is the Leaning Tower of Pisa located?',
                'number': 4,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Spain',
                'Rwer': 'Italy',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is the tallest animal in the world?',
                'number': 5,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Elephant',
                'Rwer': 'Giraffe',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is a xylophone?',
                'number': 6,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'A medical device',
                'Rwer': 'A musical instrument',
                'pic': False,
            }),
            json.dumps({
                'question': 'How many dots are on a six-sided die?',
                'number': 7,
                'round': 0,
                'topic': 'Practice',
                'Wwer': '19',
                'Rwer': '21',
                'pic': False,
            }),
            json.dumps({
                'question': 'Who wrote Hamlet?',
                'number': 8,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Leonardo da Vinci',
                'Rwer': 'William Shakespeare',
                'pic': False,
            }),
            json.dumps({
                'question': 'What year did World War II end?',
                'number': 9,
                'round': 0,
                'topic': 'Practice',
                'Wwer': '1942',
                'Rwer': '1945',
                'pic': False,
            }),
            json.dumps({
                'question': 'Ottawa is the capital of which country?',
                'number': 10,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Bolivia',
                'Rwer': 'Canada',
                'pic': False,
            }),
            json.dumps({
                'question': 'What do paleontologists study?',
                'number': 11,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Ancient human civilizations',
                'Rwer': 'Dinosaur fossils',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is a supernova?',
                'number': 12,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'An intense lightining storm',
                'Rwer': 'The explosion of a star',
                'pic': False,
            }),
            json.dumps({
                'question': 'How can bats fly in the dark?',
                'number': 13,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'X-ray vision',
                'Rwer': 'Echolocation',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is the technical term for a lie detector test?',
                'number': 14,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Seismograph',
                'Rwer': 'Polygraph',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is an echidna?',
                'number': 15,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'A Spanish dessert',
                'Rwer': 'An Australian mammal',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is the smallest country in the world?',
                'number': 16,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Monaco',
                'Rwer': 'Vatican City',
                'pic': False,
            }),
            json.dumps({
                'question': 'Who invented the light bulb?',
                'number': 17,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Alexander Graham Bell',
                'Rwer': 'Thomas Edison',
                'pic': False,
            }),
            json.dumps({
                'question': 'In Greek mythology, who is the Goddess of Agriculture?',
                'number': 18,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Persephone',
                'Rwer': 'Demeter',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is Xylography?',
                'number': 19,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'The study of hieroglyphs',
                'Rwer': 'The art of making wood engravings',
                'pic': False,
            }),
            json.dumps({
                'question': 'How many bones are in an elephant trunk?',
                'number': 20,
                'round': 0,
                'topic': 'Practice',
                'Wwer': '42',
                'Rwer': '0',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is the longest river in the world?',
                'number': 21,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Nile',
                'Rwer': 'Mississippi',
                'pic': False,
            }),
            json.dumps({
                'question': 'Which philosopher said, "I think, therefore I am"?',
                'number': 22,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Friedrich Nietzsche',
                'Rwer': 'Rene Descartes',
                'pic': False,
            }),
            json.dumps({
                'question': 'What is the chemical symbol for potassium?',
                'number': 23,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'P',
                'Rwer': 'K',
                'pic': False,
            }),json.dumps({
                'question': 'What does a mycologist study?',
                'number': 24,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Mushrooms',
                'Rwer': 'Anti-matter',
                'pic': False,
            }),json.dumps({
                'question': 'What is the head of the Roman Catholic Church called?',
                'number': 25,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Preacher',
                'Rwer': 'Pope',
                'pic': False,
            }),
            json.dumps({
                'question': 'Damascus is the capital of which country?',
                'number': 26,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Lebanon',
                'Rwer': 'Syria',
                'pic': False,
            }),
            json.dumps({
                'question': 'What do plants need light for?',
                'number': 27,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Respiration',
                'Rwer': 'Photosynthesis',
                'pic': False,
            }),
            json.dumps({
                'question': 'What do plants need light for?',
                'number': 27,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Respiration',
                'Rwer': 'Photosynthesis',
                'pic': False,
            }),
            json.dumps({
                'question': 'Which word means "severe and intense"?',
                'number': 28,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Chronic',
                'Rwer': 'Acute',
                'pic': False,
            }),
            json.dumps({
                'question': 'Which punctuation mark indicates a longer pause?',
                'number': 29,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'A comma',
                'Rwer': 'A semicolon',
                'pic': False,
            }),
            json.dumps({
                'question': 'How many different colors are on the flag of South Africa?',
                'number': 30,
                'round': 0,
                'topic': 'Practice',
                'Wwer': '9',
                'Rwer': '6',
                'pic': False,
            }),
        ]

        number_transmissions = len(self.infos())
        if number_transmissions < len(questions):
            question = questions[number_transmissions]
        else:
            question = questions[-1]
        return question
