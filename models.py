from dallinger.nodes import Source
from dallinger.models import questions


class Questionaire(Source):
    """A Source that reads in a question from a file and transmits it."""

    __mapper_args__ = {"polymorphic_identity": "questionaire_source"}

    def _contents(self):
        """Define the contents of new Infos.

        transmit() -> _what() -> create_information() -> _contents().
        """
           story = random.choice(stories)
        with open("static/stimuli/{}".format(story), "r") as f:
            return f.read()

number_transmissions = len(self.infos())
        import json
        questions = [
            json.dumps({
                'question': 'What is the capital city of France?',
                'number': 'practice 1',
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Barcelona',
                'Rwer': 'Paris',
                'pic': False,
                }),
            json.dumps({
                'question': 'How much does an average chimpanzee weigh?',
                'number': 'practice 2',
                'round': 0,
                'topic': 'Practice',
                'Wwer': '500kg',
                'Rwer': '50kg',
                'pic': False,
            })
        ]
number_transmissions = len([i for i in self.infos(questions) if i.contents not in ["Bad Luck", "Good Luck"]])
        if number_transmissions < len(questions):
            question = questions[number_transmissions]
        else:
            question = questions[-1]
        return question