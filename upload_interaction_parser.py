from json import dumps
from json import loads

from xml.dom.minidom import parseString

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring


class UploadInteraction:
    def __init__(self, identifier, prompt):
        if type(identifier) is str:
            self.identifier = identifier
        else:
            raise TypeError('Identifier needs to be a str type.')
        if type(prompt) is str:
            self.prompt = prompt
        else:
            raise TypeError('Prompt needs to be a str type.')

    def to_qti(self, adaptive='false', time_dependent='false'):
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
        nti_json = '{"Class":"Question", "MimeType":"mime_type", "NTIID":"nti_id", "content":"' + self.prompt + '", ' \
                   '"ntiid":"nti_id", "parts":[{"Class":"FilePart", "MimeType":"mime_type", ' \
                   '"allowed_extensions":[".docx", ".pdf"], "allowed_mime_types":["*/*"], "content":"", ' \
                   '"explanation":"", "hints":[], "max_file_size":10485760, "solutions":[]}]}'
        print nti_json
        parsed = loads(nti_json)
        nti_file = open(self.identifier + '.json', 'w+')
        nti_file.write(dumps(parsed, indent=4))
        nti_file.close()

