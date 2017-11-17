from copy import deepcopy

from io import open as open_file

from json import dumps
from json import loads

from re import compile as compile_pattern

from string import ascii_uppercase

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

        if len(labels) is not len(values):
            raise ValueError('labels[] must have the same length as values[]')

        self.solution_pattern = compile_pattern('(.+) (.+)')

        self.char = dict(zip(map(str, range(26)), ascii_uppercase))

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
        while solutions:
            matcher = self.solution_pattern.search(solutions[0])
            correct_response_value = SubElement(correct_response, 'value')
            correct_response_value.text = str(matcher.group(1)) + ' ' + self.char[str(matcher.group(2))]
            solutions.pop(0)
        # outcome_declaration
        SubElement(assessment_item, 'outcomeDeclaration', {'identifier': 'SCORE',
                                                           'cardinality': 'single',
                                                           'baseType': 'float'})
        item_body = SubElement(assessment_item, 'itemBody')
        match_interaction = SubElement(item_body, 'matchInteraction', {'responseIdentifier': 'RESPONSE',
                                                                       'shuffle': shuffle,
                                                                       'maxAssociations': '0'})
        prompt__sub_element = SubElement(match_interaction, 'prompt')
        prompt__sub_element.text = self.prompt
        simple_match_set_1 = SubElement(match_interaction, 'simpleMatchSet')
        identifier = 0
        while labels:
            simple_associable_choice = SubElement(simple_match_set_1, 'simpleAssociableChoice', 
                                                  {'identifier': str(identifier),
                                                   'matchMax': '1'})
            simple_associable_choice.text = labels.pop(0)
            identifier += 1
        simple_match_set_2 = SubElement(match_interaction, 'simpleMatchSet')
        identifier = 0
        while values:
            simple_associable_choice = SubElement(simple_match_set_2, 'simpleAssociableChoice',
                                                  {'identifier': self.char[str(identifier)],
                                                   'matchMax': '1'})
            simple_associable_choice.text = values.pop(0)
            identifier += 1
        # response_processing
        SubElement(assessment_item, 'responseProcessing',
                   {'template':
                       "http://www.imsglobal.org/question/qti_v2p2/rptemplates/match_correct"})

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        qti_file = open_file(self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

    def to_nti(self):
        labels = deepcopy(self.labels)
        solutions = deepcopy(self.solutions)
        values = deepcopy(self.values)

        mime_type_q = '"application/vnd.nextthought.naquestion"'
        mime_type_ma = '"application/vnd.nextthought.assessment.matchingpart"'
        mime_type_ma_s = '"application/vnd.nextthought.assessment.matchingsolution"'

        if not labels:
            raise ValueError('labels[] cannot be empty')
        
        if not solutions:
            raise ValueError('solutions[] cannot be empty')

        if not values:
            raise ValueError('values[] cannot be empty')

        nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + self.identifier + '", ' \
                   '"content":"' + self.prompt + '", "ntiid":"' + self.identifier + '", "parts":[{"Class":' \
                   '"MatchingPart", "MimeType":' + mime_type_ma + ', "content":"", "explanation":"", "hints":[],' \
                   '"labels":["'
        while labels:
            if len(labels) is 1:
                nti_json += labels.pop(0) + '"], '
            else:
                nti_json += labels.pop(0) + '", "'
        nti_json += '"solutions":[{"Class":"MatchingSolution", "MimeType":' + mime_type_ma_s + ', "value":{'
        while solutions:
            matcher = self.solution_pattern.search(solutions[0])
            if len(solutions) is 1:
                nti_json += '"' + matcher.group(1) + '":' + matcher.group(2) + '}, '
            else:
                nti_json += '"' + matcher.group(1) + '":' + matcher.group(2) + ', '
            solutions.pop(0)
        nti_json += '"weight":1.0}], "values":["'
        while values:
            if len(values) is 1:
                nti_json += values.pop(0) + '"]}]}'
            else:
                nti_json += values.pop(0) + '", "'

        parsed = loads(nti_json)

        nti_file = open_file(self.title + '.json', 'w+', encoding="utf-8")
        nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
        nti_file.close()
