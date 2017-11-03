from copy import deepcopy

from io import open

from json import dumps
from json import loads

from xml.dom.minidom import parseString

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring


class MatchInteraction(object):

    def __init__(self, identifier, prompt, title, labels, solutions, values):
        if type(identifier) is str:
            self.identifier = identifier
        else:
            raise TypeError('identifier needs to be a str type')

        if type(prompt) is str:
            self.prompt = prompt
        else:
            raise TypeError('prompt needs to be a str type')

        if type(title) is str:
            if not title:
                self.title = identifier
            else:
                self.title = title
        else:
            raise TypeError('title needs to be a str type')

        if type(labels) is list:
            self.labels = labels
        else:
            raise TypeError('labels[] needs to be a list type')

        if type(solutions) is list:
            self.solutions = solutions
        else:
            raise TypeError('solutions[] needs to be a list type')

        if type(values) is list:
            self.values = values
        else:
            raise TypeError('values[] needs to be a list type')

        if not identifier:
            raise ValueError('identifier cannot be empty')

        if not prompt:
            raise ValueError('prompt cannot be empty')

        if not labels:
            raise ValueError('labels[] cannot be empty')

        if not solutions:
            raise ValueError('solutions[] cannot be empty')

        if not values:
            raise ValueError('values[] cannot be empty')

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
        labels = deepcopy(self.labels)
        solutions = deepcopy(self.solutions)
        values = deepcopy(self.values)

        if not labels:
            raise ValueError('labels[] cannot be empty')

        if not solutions:
            raise ValueError('solutions[] cannot be empty')

        if not values:
            raise ValueError('values[] cannot be empty')

        assessment_item = Element('assessmentItem', {'xmlns': "http://www.imsglobal.org/xsd/imsqti_v2p2",
                                                     'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                                     'xsi:schemaLocation':
                                                         "http://www.imsglobal.org/xsd/imsqti_v2p2 "
                                                         "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd",
                                                     'identifier': self.identifier,
                                                     'title': self.title,
                                                     'adaptive': adaptive,
                                                     'timeDependent': time_dependent})
        response_declaration = SubElement(assessment_item, 'responseDeclaration',
                                          {'identifier': 'RESPONSE',
                                           'cardinality': 'multiple',
                                           'baseType': 'directedPair'})
        correct_response = SubElement(response_declaration, 'correctResponse')
        while values:
            correct_response_value = SubElement(correct_response, 'value')
            correct_response_value.text = self.char[values.pop(0)]
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
        while choices:
            simple_choice = SubElement(choice_interaction, 'simpleChoice', {'identifier':
                                                                            str(self.char[str(identifier)])})
            simple_choice.text = choices.pop(0)
            identifier += 1
        response_processing = SubElement(assessment_item, 'responseProcessing',
                                         {'template':
                                             "http://www.imsglobal.org/question/qti_v2p2/rptemplates/match_correct"})

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        qti_file = open('/QTI_Questions/matchInteraction_Questions/' + self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

    def to_nti(self):
        choices = deepcopy(self.choices)
        values = deepcopy(self.values)

        mime_type_q = '"application/vnd.nextthought.naquestion"'
        mime_type_ma = '"application/vnd.nextthought.assessment.matchingpart"'
        mime_type_ma_s = '"application/vnd.nextthought.assessment.multiplechoicemultipleanswerpart"'

        if not choices:
            raise ValueError('Choices[] cannot be empty.')

        if not values:
            raise ValueError('Values[] cannot be empty.')

        if type(int(values[0])) is not int:
            for place, value in enumerate(values):
                value = str(self.char.keys()[self.char.values().index(values[place])])
                values[place] = value

        nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + self.identifier + '", ' \
                   '"content":"' + self.prompt + '", "ntiid":"' + self.identifier + '", "parts":[{"Class":' \
                   '"MultipleChoiceMultipleAnswerPart, "MimeType":' + mime_type_ma + ', "choices":['
        while choices:
            if len(choices) is 1:
                nti_json += choices.pop(0) + '], '
            else:
                nti_json += choices.pop(0) + ', '
        nti_json += '"content":"", "explanation":"", "hints":[], "solutions":[{"Class":' \
                    '"MultipleChoiceMultipleAnswerSolution", "MimeType":' + mime_type_ma_s + ', "value":'
        if len(values) is 1:
            nti_json += values.pop(0) + ', '
        else:
            nti_json += '['
            while values:
                if len(values) is 1:
                    nti_json += values.pop(0) + '], '
                else:
                    nti_json += values.pop(0) + ', '
        nti_json += '"weight":1.0}]}]}'

        parsed = loads(nti_json)

        nti_file = open('/NTI_Questions/MatchingPart_Questions/' + self.title + '.json', 'w+', encoding="utf-8")
        nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
        nti_file.close()
