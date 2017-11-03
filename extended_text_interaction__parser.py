from io import open

from json import dumps
from json import loads

from xml.dom.minidom import parseString

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring


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
        response_declaration = SubElement(assessment_item, 'responseDeclaration',
                                          {'identifier': 'RESPONSE',
                                           'cardinality': 'single',
                                           'baseType': 'string'})
        outcome_declaration = SubElement(assessment_item, 'outcomeDeclaration', {'identifier': 'SCORE',
                                                                                 'cardinality': 'single',
                                                                                 'baseType': 'float',
                                                                                 'externalScored': 'human'})
        item_body = SubElement(assessment_item, 'itemBody')
        extended_text_interaction = SubElement(item_body, 'extendedTextInteraction', {'responseIdentifier': 'RESPONSE'})
        prompt__sub_element = SubElement(extended_text_interaction, 'prompt')
        prompt__sub_element.text = self.prompt

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        qti_file = open('/QTI_Questions/extendedTextInteractions_Questions/' + self.title + '.xml', 'w+', encoding="utf-8")
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

        nti_file = open('/NTI_Questions/ModeledContentPart_Questions/' + self.title + '.json', 'w+', encoding="utf-8")
        nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
        nti_file.close()
