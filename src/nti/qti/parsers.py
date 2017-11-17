from copy import deepcopy

from io import open as open_file

from json import dumps
from json import loads

from re import split

from string import ascii_uppercase

from xml.dom.minidom import parseString

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring


class ChoiceInteraction(object):

    def __init__(self, identifier, prompt, title, values, choices):
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

        if type(values) is list:
            self.values = values
        else:
            raise TypeError('values[] needs to be a list type')

        if type(choices) is list:
            self.choices = choices
        else:
            raise TypeError('choices[] needs to be a list type')

        if not identifier:
            raise ValueError('identifier cannot be empty')

        if not prompt:
            raise ValueError('prompt cannot be empty')

        if len(values) > 1:
            self.multiple_answer = True
        elif len(values) == 1:
            self.multiple_answer = False
        else:
            raise ValueError('values[] cannot be empty')

        if not choices:
            raise ValueError('choices[] cannot be empty')

        self.char = dict(zip(map(str, range(26)), ascii_uppercase))

    def to_qti(self, adaptive='false', time_dependent='false', shuffle='false'):
        choices = deepcopy(self.choices)
        values = deepcopy(self.values)

        if not choices:
            raise ValueError('choices[] cannot be empty')

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
                                           'cardinality':
                                               'multiple' if self.multiple_answer else 'single',
                                           'baseType': 'identifier'})
        correct_response = SubElement(response_declaration, 'correctResponse')
        while values:
            correct_response_value = SubElement(correct_response, 'value')
            correct_response_value.text = self.char[values.pop(0)]
        # outcome_declaration
        SubElement(assessment_item, 'outcomeDeclaration', {'identifier': 'SCORE',
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
        # response_processing
        SubElement(assessment_item, 'responseProcessing',
                   {'template': "http://www.imsglobal.org/question/qti_v2p2/rptemplates/match_correct"})

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        qti_file = open_file('/QTI_Questions/choiceInteraction_Questions/'
                             + self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

    def to_nti(self):
        choices = deepcopy(self.choices)
        values = deepcopy(self.values)

        mime_type_q = '"application/vnd.nextthought.naquestion"'
        mime_type_mc = '"application/vnd.nextthought.assessment.multiplechoicepart"'
        mime_type_mc_ma = '"application/vnd.nextthought.assessment.multiplechoicemultipleanswerpart"'
        mime_type_mc_s = '"application/vnd.nextthought.assessment.multiplechoicesolution"'
        mime_type_mc_ma_s = '"application/vnd.nextthought.assessment.multiplechoicemultipleanswersolution"'

        if not choices:
            raise ValueError('choices[] cannot be empty')

        if not values:
            raise ValueError('values[] cannot be empty')

        if type(int(values[0])) is not int:
            for place, value in enumerate(values):
                value = str(self.char.keys()[self.char.values().index(values[place])])
                values[place] = value

        nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + self.identifier + '", ' \
                   '"content":"' + self.prompt + '", "ntiid":"' + self.identifier + '", "parts":[{"Class":' + \
                   ('"MultipleChoiceMultipleAnswerPart"' if self.multiple_answer else '"MultipleChoicePart"') + ', ' \
                   '"MimeType":' + (mime_type_mc_ma if self.multiple_answer else mime_type_mc) + ', "choices":['
        while choices:
            if len(choices) is 1:
                nti_json += choices.pop(0) + '], '
            else:
                nti_json += choices.pop(0) + ', '
        nti_json += '"content":"", "explanation":"", "hints":[], "solutions":[{"Class":' + \
                    ('"MultipleChoiceMultipleAnswerSolution"' if self.multiple_answer else '"MultipleChoiceSolution"') \
                    + ', "MimeType":' + (mime_type_mc_ma_s if self.multiple_answer else mime_type_mc_s) + ', "value":'
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

        nti_file = \
            open_file('/NTI_Questions/' + ('MultipleChoiceMultipleAnswer' if self.multiple_answer else 'MultipleChoice')
                      + 'Part_Questions/' + self.title + '.json', 'w+', encoding="utf-8")
        nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
        nti_file.close()


class ExtendedTextInteraction(object):

    def __init__(self, identifier, prompt, title):
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

        if not identifier:
            raise ValueError('identifier cannot be empty')

        if not prompt:
            raise ValueError('prompt cannot be empty')

    def to_qti(self, adaptive='false', time_dependent='false'):
        assessment_item = Element('assessmentItem', {'xmlns': "http://www.imsglobal.org/xsd/imsqti_v2p2",
                                                     'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                                     'xsi:schemaLocation':
                                                         "http://www.imsglobal.org/xsd/imsqti_v2p2 "
                                                         "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd",
                                                     'identifier': self.identifier,
                                                     'title': self.title,
                                                     'adaptive': adaptive,
                                                     'timeDependent': time_dependent})
        # response_declaration
        SubElement(assessment_item, 'responseDeclaration',
                                    {'identifier': 'RESPONSE',
                                     'cardinality': 'single',
                                     'baseType': 'string'})
        # outcome_declaration
        SubElement(assessment_item, 'outcomeDeclaration', {'identifier': 'SCORE',
                                                           'cardinality': 'single',
                                                           'baseType': 'float',
                                                           'externalScored': 'human'})
        item_body = SubElement(assessment_item, 'itemBody')
        extended_text_interaction = SubElement(item_body, 'extendedTextInteraction', {'responseIdentifier': 'RESPONSE'})
        prompt__sub_element = SubElement(extended_text_interaction, 'prompt')
        prompt__sub_element.text = self.prompt

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        qti_file = open_file('/QTI_Questions/extendedTextInteractions_Questions/'
                             + self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

    def to_nti(self):
        mime_type_q = '"application/vnd.nextthought.naquestion"'
        mime_type_model = '"application/vnd.nextthought.assessment.modeledcontentpart"'

        nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + self.identifier + '", ' \
                   '"content":"' + self.prompt + '", "ntiid":"' + self.identifier + '", ' \
                   '"parts":[{"Class":"ModeledContentPart", "MimeType":' + mime_type_model + ', "content":"", ' \
                   '"explanation":"", "hints":[], "solutions":[]}]}'

        parsed = loads(nti_json)

        nti_file = open_file('/NTI_Questions/ModeledContentPart_Questions/'
                             + self.title + '.json', 'w+', encoding="utf-8")
        nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
        nti_file.close()


class TextEntryInteraction(object):

    def __init__(self, identifier, prompt, title, values, math=False):
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

        if type(math) is bool:
            self.math = math
        else:
            raise TypeError('math needs to be a bool type')

        if not self.math:
            if type(values) is list:
                self.values = values
            else:
                raise TypeError('values[] needs to be a list type')
        if self.math:
            if type(values) is str:
                self.values = values
            else:
                raise TypeError('values needs to be a str type')

        if not identifier:
            raise ValueError('identifier cannot be empty')

        if not prompt:
            raise ValueError('prompt cannot be empty')

        if not self.math:
            if not values:
                raise ValueError('values[] cannot be empty')
        if self.math:
            if not values:
                raise ValueError('values cannot be empty')

    def to_qti(self, adaptive='false', time_dependent='false'):
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
                                                     'adaptive': adaptive,
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
                # map_entry
                SubElement(mapping, 'mapEntry', {'mapKey': values.pop(0), 'mappedValue': '1'})
        if self.math:
            correct_response_value.text = self.values
        # outcome_declaration
        SubElement(assessment_item, 'outcomeDeclaration', {'identifier': 'SCORE',
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
        if not self.math:
            # response_processing
            SubElement(assessment_item, 'responseProcessing',
                       {'template': 'http://www.imsglobal.org/question/qti_v2p2/rptemplates/map_response'})
        if self.math:
            # response_processing
            SubElement(assessment_item, 'responseProcessing',
                       {'template': 'http://www.imsglobal.org/question/qti_v2p2/rptemplates/match_correct'})

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        qti_file = open_file('/QTI_Questions/textEntryInteraction_Questions/'
                             + self.title + '.xml', 'w+', encoding="utf-8")
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

            nti_file = open_file('/NTI_Questions/SymbolicMathPart_Questions/'
                                 + self.title + '.json', 'w+', encoding="utf-8")
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

            nti_file = open_file('/NTI_Questions/FreeResponsePart_Questions/'
                                 + self.title + '.json', 'w+', encoding="utf-8")
            nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
            nti_file.close()


class UploadInteraction(object):

    def __init__(self, identifier, prompt, title):
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
                self.title = title
            else:
                self.title = identifier
        else:
            raise TypeError('title needs to be a str type')

        if not identifier:
            raise ValueError('identifier cannot be empty')

        if not prompt:
            raise ValueError('prompt cannot be empty')

    def to_qti(self, adaptive='false', time_dependent='false'):
        assessment_item = Element('assessmentItem', {'xmlns': "http://www.imsglobal.org/xsd/imsqti_v2p2",
                                                     'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                                     'xsi:schemaLocation':
                                                         "http://www.imsglobal.org/xsd/imsqti_v2p2 "
                                                         "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd",
                                                     'identifier': self.identifier,
                                                     'title': self.title,
                                                     'adaptive': adaptive,
                                                     'timeDependent': time_dependent})
        # response_declaration
        SubElement(assessment_item, 'responseDeclaration',
                                    {'identifier': 'RESPONSE',
                                     'cardinality': 'single',
                                     'baseType': 'file'})
        # outcome_declaration
        SubElement(assessment_item, 'outcomeDeclaration', {'identifier': 'SCORE',
                                                           'cardinality': 'single',
                                                           'baseType': 'float'})
        item_body = SubElement(assessment_item, 'itemBody')
        upload_interaction = SubElement(item_body, 'uploadInteraction', {'responseIdentifier': 'RESPONSE'})
        prompt__sub_element = SubElement(upload_interaction, 'prompt')
        prompt__sub_element.text = self.prompt

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        qti_file = open_file('/QTI_Questions/uploadInteraction_Questions/'
                             + self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

    def to_nti(self):
        mime_type_q = '"application/vnd.nextthought.naquestion"'
        mime_type_f = '"application/vnd.nextthought.assessment.filepart"'

        nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + self.identifier + '", ' \
                   '"content":"' + self.prompt + '", "ntiid":"' + self.identifier + '", ' \
                   '"parts":[{"Class":"FilePart", "MimeType":' + mime_type_f + ', ' \
                   '"allowed_extensions":[".docx", ".pdf"], "allowed_mime_types":["*/*"], "content":"", ' \
                   '"explanation":"", "hints":[], "max_file_size":10485760, "solutions":[]}]}'

        parsed = loads(nti_json)

        nti_file = open_file('/NTI_Questions/FilePart_Questions/' + self.title + '.json', 'w+', encoding="utf-8")
        nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
        nti_file.close()