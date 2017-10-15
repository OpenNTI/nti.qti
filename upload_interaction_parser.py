from json import dumps
from json import loads

from xml.dom.minidom import parseString

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring


class UploadInteraction:

    def __init__(self, identifier, prompt, title=''):
        if type(identifier) is str:
            self.identifier = identifier
        else:
            raise TypeError('Identifier needs to be a str type.')

        if type(prompt) is str:
            self.prompt = prompt
        else:
            raise TypeError('Prompt needs to be a str type.')

        if type(title) is str:
            if title is not '':
                self.title = title
            else:
                self.title = identifier
        else:
            raise TypeError('Title needs to be a str type.')

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
                                           'baseType': 'file'})
        outcome_declaration = SubElement(assessment_item, 'outcomeDeclaration', {'identifier': 'SCORE',
                                                                                 'cardinality': 'single',
                                                                                 'baseType': 'float'})
        item_body = SubElement(assessment_item, 'itemBody')
        upload_interaction = SubElement(item_body, 'uploadInteraction', {'responseIdentifier': 'RESPONSE'})
        prompt__sub_element = SubElement(upload_interaction, 'prompt')
        prompt__sub_element.text = self.prompt

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)
        qti_file = open(self.identifier + '.xml', 'w+')
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

        nti_file = open(self.identifier + '.json', 'w+')
        nti_file.write(dumps(parsed, indent=4))
        nti_file.close()
