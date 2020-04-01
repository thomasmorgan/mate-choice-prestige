from dallinger.nodes import Source
import json


class Questionnaire(Source):
    """A Source that reads in a question from a file and transmits it."""

    __mapper_args__ = {"polymorphic_identity": "questionnaire_source"}

    def _contents(self):
        """Define the contents of new Infos.

        transmit() -> _what() -> create_information() -> _contents().
        """
        questions = [
            json.dumps({
                'question': 'What is the capital city of France?',
                'number': 1,
                'round': 0,
                'topic': 'Practice',
                'Wwer': 'Barcelona',
                'Rwer': 'Paris',
                'pic': False,
            }),
            json.dumps({
                'question': 'How much does an average chimpanzee weigh?',
                'number': 2,
                'round': 0,
                'topic': 'Practice',
                'Wwer': '500kg',
                'Rwer': '50kg',
                'pic': False,
            })
        ]

        number_transmissions = len(self.infos())
        if number_transmissions < len(questions):
            question = questions[number_transmissions]
        else:
            question = questions[-1]
        return question
