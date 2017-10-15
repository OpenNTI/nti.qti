from copy import deepcopy

from json import dumps
from json import loads

from xml.dom.minidom import parseString

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring


class ChoiceInteraction:
    def __init__(self, identifier, prompt, correct, choice):
        if type(identifier) is str:
            self.identifier = identifier
        else:
            raise TypeError('Identifier needs to be a str type.')
        if type(prompt) is str:
            self.prompt = prompt
        else:
            raise TypeError('Prompt needs to be a str type.')
        if type(correct) is list:
            self.correct = correct
        else:
            raise TypeError('Correct[] needs to be a list type.')
        if type(choice) is list:
            self.choice = choice
        else:
            raise TypeError('Choice[] needs to be a list type.')
        if len(correct) > 1:
            self.multiple_answer = True
        elif len(correct) == 1:
            self.multiple_answer = False
        else:
            raise ValueError('Correct[] cannot be empty.')
        if len(choice) <= 0:
            raise ValueError('Choice[] cannot be empty.')
        self.char = {
            '0': 'ChoiceA',
            '1': 'ChoiceB',
            '2': 'ChoiceC',
            '3': 'ChoiceD',
            '4': 'ChoiceE',
            '5': 'ChoiceF',
            '6': 'ChoiceG',
            '7': 'ChoiceH',
            '8': 'ChoiceI',
            '9': 'ChoiceJ',
            '10': 'ChoiceK',
            '11': 'ChoiceL',
            '12': 'ChoiceM',
            '13': 'ChoiceN',
            '14': 'ChoiceO',
            '15': 'ChoiceP',
            '16': 'ChoiceQ',
            '17': 'ChoiceR',
            '18': 'ChoiceS',
            '19': 'ChoiceT',
            '20': 'ChoiceU',
            '21': 'ChoiceV',
            '22': 'ChoiceW',
            '23': 'ChoiceX',
            '24': 'ChoiceY',
            '25': 'ChoiceZ',
        }

    def to_qti(self, adaptive='false', time_dependent='false', shuffle='false'):
        choice = deepcopy(self.choice)
        correct = deepcopy(self.correct)
        if len(choice) <= 0:
            raise ValueError('Choice[] cannot be empty.')
        if len(correct) <= 0:
            raise ValueError('Correct[] cannot be empty.')
        assessment_item = Element('assessmentItem', {'xmlns': "http://www.imsglobal.org/xsd/imsqti_v2p2",
                                                     'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                                     'xsi:schemaLocation':
                                                         "http://www.imsglobal.org/xsd/imsqti_v2p2 "
                                                         "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd",
                                                     'identifier': self.identifier,
                                                     'title': self.identifier,
                                                     'adaptive': adaptive,
                                                     'timeDependent': time_dependent})
        response_declaration = SubElement(assessment_item, 'responseDeclaration',
                                          {'identifier': 'RESPONSE',
                                           'cardinality':
                                               'multiple' if self.multiple_answer else 'single',
                                           'baseType': 'identifier'})
        correct_response = SubElement(response_declaration, 'correctResponse')
        while len(correct) is not 0:
            correct_response_value = SubElement(correct_response, 'value')
            correct_response_value.text = self.char[correct.pop(0)]
            outcome_declaration = SubElement(assessment_item, 'outcomeDeclaration', {'identifier': 'SCORE',
                                                                                     'cardinality': 'single',
                                                                                     'baseType': 'float'})
        item_body = SubElement(assessment_item, 'itemBody')
        choice_interaction = SubElement(item_body, 'choiceInteraction', {'responseIdentifier': 'RESPONSE',
                                                                         'shuffle': shuffle,
                                                                         'maxChoices':
                                                                             '0' if self.multiple_answer else '1'})
        prompt__sub_element = SubElement(choice_interaction, 'prompt')
        prompt__sub_element.text = self.prompt
        identifier = 0
        while len(choice) is not 0:
            simple_choice = SubElement(choice_interaction, 'simpleChoice', {'identifier':
                                                                            str(self.char[str(identifier)])})
            simple_choice.text = choice.pop(0)
            identifier += 1
        response_processing = SubElement(assessment_item, 'responseProcessing',
                                         {'template':
                                             "http://www.imsglobal.org/question/qti_v2p2/rptemplates/match_correct"})
        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)
        qti_file = open(self.identifier + '.xml', 'w+')
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

    def to_nti(self):
        choice = deepcopy(self.choice)
        correct = deepcopy(self.correct)
        if len(choice) <= 0:
            raise ValueError('Choice[] cannot be empty.')
        if len(correct) <= 0:
            raise ValueError('Correct[] cannot be empty.')
        if type(int(correct[0])) is not int:
            for place, value in enumerate(correct):
                value = str(self.char.keys()[self.char.values().index(correct[place])])
                correct[place] = value
        nti_json = '{"Class":"Question", "MimeType":"mime_type", "NTIID":"nti_id", "content":"' + self.prompt + '", ' \
                   '"ntiid":"nti_id", "parts":[{"Class":' + \
                   ('"MultipleChoiceMultipleAnswerPart"' if self.multiple_answer else '"MultipleChoicePart"') + ', ' \
                   '"MimeType":"mime_type", "choices":["'
        while len(choice) is not 0:
            if len(choice) is 1:
                nti_json += choice.pop(0) + '"], '
            else:
                nti_json += choice.pop(0) + '", "'
        nti_json += '"content":"", "explanation":"", "hints":[], "solutions":[{"Class":' + \
                    ('"MultipleChoiceMultipleAnswerSolution"' if self.multiple_answer else '"MultipleChoiceSolution"') \
                    + ', "MimeType":"mime_type", "value":['
        while len(correct) is not 0:
            if len(correct) is 1:
                nti_json += correct.pop(0) + '], '
            else:
                nti_json += correct.pop(0) + ', '
        nti_json += '"weight":1.0}]}]}'
        parsed = loads(nti_json)
        nti_file = open(self.identifier + '.json', 'w+')
        nti_file.write(dumps(parsed, indent=4))
        nti_file.close()

