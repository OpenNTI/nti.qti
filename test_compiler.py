# noinspection PyUnresolvedReferences
from binascii import b2a_hex

from datetime import datetime

from io import open as open_file

from os import listdir
from os import urandom

from xml.dom.minidom import parseString

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring


class TestCompiler(object):
    def __init__(self, identifier, title, author='author'):
        if type(identifier) is str:
            self.identifier = identifier
        else:
            raise TypeError('identifier needs to be a str type')

        if type(title) is str:
            if not title:
                self.title = identifier
            else:
                self.title = title
        else:
            raise TypeError('title needs to be a str type')

        if type(author) is str:
            self.author = author
        else:
            raise TypeError('author needs to be a str type')

    def compile(self, directory, max_score=100):
        if type(directory) is not str:
            raise TypeError('directory needs to be a str type')

        if type(max_score) is not int:
            raise TypeError('directory needs to be an int type')

        assessment_test = Element('assessmentTest', {'xmlns': "http://www.imsglobal.org/xsd/imsqti_v2p2",
                                                     'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                                     'xsi:schemaLocation':
                                                         "http://www.imsglobal.org/xsd/imsqti_v2p2 "
                                                         "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd",
                                                     'identifier': self.identifier,
                                                     'title': self.title})
        outcome_declaration__score = SubElement(assessment_test, 'outcomeDeclaration', {'identifier': "SCORE",
                                                                                        'cardinality': 'single',
                                                                                        'baseType': 'float'})
        default_value__score = SubElement(outcome_declaration__score, 'defaultValue')
        value__score = SubElement(default_value__score, 'value')
        value__score.text = str(0.0)
        outcome_declaration__max_score = SubElement(assessment_test, 'outcomeDeclaration', {'identifier': "SCORE",
                                                                                            'cardinality': 'single',
                                                                                            'baseType': 'float'})
        default_value__max_score = SubElement(outcome_declaration__max_score, 'defaultValue')
        value__max_score = SubElement(default_value__max_score, 'value')
        value__max_score.text = str(max_score)
        test_part = SubElement(assessment_test, 'testPart', {'identifier': "testpartID",
                                                             'navigationMode': "nonlinear",
                                                             'submissionMode': "individual"})
        assessment_section = SubElement(test_part, 'assessmentSection', {'identifier': "sectionID",
                                                                         'fixed': "false",
                                                                         'title': "sectionTitle",
                                                                         'visible': "false"})
        for filename in listdir(directory):
            # assessment_item_ref
            SubElement(assessment_section, 'assessmentItemRef', {'identifier': filename.replace('.xml', ''),
                                                                 'href': filename,
                                                                 'fixed': "false"})
        outcome_processing = SubElement(assessment_test, 'outcomeProcessing')
        set_outcome_value = SubElement(outcome_processing, 'setOutcomeValue', {'identifier': "SCORE"})
        sum_element = SubElement(set_outcome_value, 'sum')
        # test_variables
        SubElement(sum_element, 'testVariables', {'variableIdentifier': "SCORE"})

        rough_string = tostring(assessment_test)
        reparsed = parseString(rough_string)

        qti_file = open_file(self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

        self.manifest(directory)

    def manifest(self, directory):

        manifest = Element('manifest', {'xmlns': "http://www.imsglobal.org/xsd/imsqti_v2p2",
                                        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                        'xsi:schemaLocation':
                                            "http://www.imsglobal.org/xsd/imsqti_v2p2 "
                                            "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd "
                                            "http://www.imsglobal.org/xsd/imscp_v1p1 "
                                            "http://www.imsglobal.org/xsd/qti/qtiv2p1/qtiv2p1_imscpv1p2_v1p0.xsd "
                                            "http://www.imsglobal.org/xsd/imsqti_v2p1 "
                                            "http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_v2p1p1.xsd "
                                            "http://www.imsglobal.org/xsd/imsqti_metadata_v2p1 "
                                            "http://www.imsglobal.org/xsd/qti/qtiv2p1/imsqti_metadata_v2p1p1.xsd "
                                            "http://ltsc.ieee.org/xsd/LOM "
                                            "http://www.imsglobal.org/xsd/imsmd_loose_v1p3p2.xsd "
                                            "http://www.w3.org/1998/Math/MathML "
                                            "http://www.w3.org/Math/XMLSchema/mathml2/mathml2.xsd",
                                        'identifier': self.identifier + '_manifest'})
        metadata = SubElement(manifest, 'metadata')
        schema = SubElement(metadata, 'schema')
        schema.text = 'QTIv2.2 Package'
        schema_version = SubElement(metadata, 'schemaversion')
        schema_version.text = '1.0.0'
        # organizations
        SubElement(manifest, 'organizations')
        resources = SubElement(manifest, 'resources')
        resource = SubElement(resources, 'resource', {'identifier': self.identifier,
                                                      'type': 'imsqti_test_xmlv2p2',
                                                      'href': self.identifier + '.xml'})
        metadata_resource = SubElement(resource, 'metadata')
        lom = SubElement(metadata_resource, 'lom', {'xmls': "http://ltsc.ieee.org/xsd/LOM"})
        general = SubElement(lom, 'general')
        identifier = SubElement(general, 'identifier')
        entry = SubElement(identifier, 'entry')
        entry.text = self.identifier
        title = SubElement(general, 'title')
        string = SubElement(title, 'string', {'language': "en"})
        string.text = self.title
        life_cycle = SubElement(lom, 'lifeCycle')
        contribute = SubElement(life_cycle, 'contribute')
        date = SubElement(contribute, 'date')
        date_time = SubElement(date, 'dateTime')
        date_time.text = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        role = SubElement(contribute, 'role')
        source = SubElement(role, 'source')
        source.text = 'LOMv1.0'
        value = SubElement(role, 'value')
        value.text = self.author
        entity = SubElement(life_cycle, 'entity')
        entity.text = b2a_hex(urandom(16))
        educational = SubElement(lom, 'educational')
        learning_resource_type = SubElement(educational, 'learningResourceType')
        source = SubElement(learning_resource_type, 'source')
        source.text = 'QTIv2.2'
        value = SubElement(learning_resource_type, 'value')
        value.text = 'ExaminationTest'
        # file
        SubElement(resource, 'file', {'href': self.identifier + '.xml'})
        for filename in listdir(directory):
            # dependency
            SubElement(resource, 'dependency', {'identifierref': filename.replace('.xml', '')})
            resource_file = SubElement(resources, 'resource', {'identifier': filename.replace('.xml', ''),
                                                               'type': 'imsqti_test_xmlv2p2',
                                                               'href': filename})
            # file
            SubElement(resource_file, 'file', {'href': filename})

        rough_string = tostring(manifest)
        reparsed = parseString(rough_string)

        qti_file = open_file(self.title + '_manifest.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()
