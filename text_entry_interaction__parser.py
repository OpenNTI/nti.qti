from copy import deepcopy

from io import open

from json import dumps
from json import loads

from re import split

from xml.dom.minidom import parseString

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring


class TextEntryInteraction(object):

    def __init__(self, identifier, prompt, title, values, math=False):
        if type(identifier) is str:
            self.identifier = identifier
        else:
            raise TypeError('Identifier needs to be a str type.')

        if type(prompt) is str:
            self.prompt = prompt
        else:
            raise TypeError('Prompt needs to be a str type.')

        if type(title) is str:
            if not title:
                self.title = identifier
            else:
                self.title = title
        else:
            raise TypeError('Title needs to be a str type.')

        if type(math) is bool:
            self.math = math
        else:
            raise TypeError('Math needs to be a bool type.')

        if not self.math:
            if type(values) is list:
                self.values = values
            else:
                raise TypeError('Values[] needs to be a list type.')
        if self.math:
            if type(values) is str:
                self.values = values
            else:
                raise TypeError('Values needs to be a str type.')

        if not identifier:
            raise ValueError('Identifier cannot be empty.')

        if not prompt:
            raise ValueError('Prompt cannot be empty.')

        if not self.math:
            if not values:
                raise ValueError('Values[] cannot be empty.')
        if self.math:
            if not values:
                raise ValueError('Values cannot be empty.')

    def to_qti(self, time_dependent='false'):
        length = str(len(self.values))
        new_prompt = split('_+', self.prompt)
        values = deepcopy(self.values)

        if not self.math:
            length = str(self.prompt.count('_'))

        assessment_item = Element('assessmentItem', {'xmlns': "http://www.imsglobal.org/xsd/imsqti_v2p2",
                                                     'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                                     'xsi:schemaLocation':
                                                         "http://www.imsglobal.org/xsd/imsqti_v2p2 "
                                                         "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd",
                                                     'identifier': self.identifier,
                                                     'title': self.title,
                                                     'timeDependent': time_dependent})
        response_declaration = SubElement(assessment_item, 'responseDeclaration',
                                          {'identifier': 'RESPONSE',
                                           'cardinality': 'single',
                                           'baseType': 'string'})
        correct_response = SubElement(response_declaration, 'correctResponse')
        correct_response_value = SubElement(correct_response, 'value')
        if not self.math:
            correct_response_value.text = values[0]
            mapping = SubElement(response_declaration, 'mapping')
            while values:
                map_entry = SubElement(mapping, 'mapEntry', {'mapKey': values.pop(0), 'mappedValue': '1'})
        if self.math:
            correct_response_value.text = self.values
        outcome_declaration = SubElement(assessment_item, 'outcomeDeclaration', {'identifier': 'SCORE',
                                                                                 'cardinality': 'single',
                                                                                 'baseType': 'float'})
        item_body = SubElement(assessment_item, 'itemBody')
        p = SubElement(item_body, 'p')
        if not self.math:
            p.text = new_prompt.pop(0)
        if self.math:
            p.text = self.prompt
        text_entry_interaction = SubElement(p, 'textEntryInteraction', {'responseIdentifier': 'RESPONSE',
                                                                        'expectedLength': length})
        if not self.math and new_prompt:
            text_entry_interaction.tail = new_prompt.pop(0)
        response_processing = \
            SubElement(assessment_item, 'responseProcessing',
                       {'template': 'http://www.imsglobal.org/question/qti_v2p2/rptemplates/map_response'})

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        qti_file = open(self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

    def to_nti(self):
        if not self.math:
            values = deepcopy(self.values)

            mime_type_q = '"application/vnd.nextthought.naquestion"'
            mime_type_f = '"application/vnd.nextthought.assessment.freeresponsepart"'
            mime_type_f_s = '"application/vnd.nextthought.assessment.freeresponsesolution"'

            nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + self.identifier + '", ' \
                       '"content":"' + self.prompt + '", "ntiid":"' + self.identifier + '", ' \
                       '"parts":[{"Class":"FreeResponsePart", "MimeType":' + mime_type_f + ', "content":"", ' \
                       '"explanation":"", "hints":[], "solutions":['
            while values:
                if len(values) == 1:
                    nti_json += '{"Class":"FreeResponseSolution", "MimeType":' + mime_type_f_s + ', "value":"'\
                                + values.pop(0) + '", "weight":1.0}]}]}'
                else:
                    nti_json += '{"Class":"FreeResponseSolution", "MimeType":' + mime_type_f_s + ', "value":"' \
                                + values.pop(0) + '", "weight":1.0},'

            parsed = loads(nti_json)

            nti_file = open(self.title + '.json', 'w+', encoding="utf-8")
            nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
            nti_file.close()

        if self.math:
            mime_type_q = '"application/vnd.nextthought.naquestion"'
            mime_type_s_m = '"application/vnd.nextthought.assessment.symbolicmathpart"'
            mime_type_s_m_s = '"application/vnd.nextthought.assessment.latexsymbolicmathsolution"'

            nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + self.identifier + '", ' \
                       '"content":"' + self.prompt + '", "ntiid":"' + self.identifier + '", ' \
                       '"parts":[{"Class":"SymbolicMathPart", "MimeType":' + mime_type_s_m + ', "allowed_units":[""], '\
                       '"content":"", "explanation":"", "hints":[], "solutions":[{"Class":"LatexSymbolicMathSolution",'\
                       ' "MimeType":' + mime_type_s_m_s + ', "allowed_units":[""], "value":"' + self.values + '", ' \
                       '"weight":1.0}]}]}'

            parsed = loads(nti_json)

            nti_file = open(self.title + '.json', 'w+', encoding="utf-8")
            nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
            nti_file.close()
