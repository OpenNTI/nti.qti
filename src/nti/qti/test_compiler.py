from io import open as open_file

from xml.dom.minidom import parseString

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring


class TestCompiler(object):
    def __init__(self, identifier, title):
        if type(identifier) is str:
            self.identifier = identifier
        else:
            raise TypeError('Identifier needs to be a str type.')

        if type(title) is str:
            if not title:
                self.title = identifier
            else:
                self.title = title
        else:
            raise TypeError('Title needs to be a str type.')

    def compile(self):
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
        value__score = SubElement(default_value__score, 'defaultValue')
        value__score.text = str(0.0)
        outcome_declaration__max_score = SubElement(assessment_test, 'outcomeDeclaration', {'identifier': "SCORE",
                                                                                            'cardinality': 'single',
                                                                                            'baseType': 'float'})
        default_value__max_score = SubElement(outcome_declaration__max_score, 'defaultValue')
        value__max_score = SubElement(default_value__max_score, 'defaultValue')
        value__max_score.text = str(1.0)
        test_part = SubElement(assessment_test, 'testPart', {'identifier': "testpartID",
                                                             'navigationMode': "nonlinear",
                                                             'submissionMode': "individual"})
        assessment_section = SubElement(test_part, 'assessmentSection', {'identifier': "sectionID",
                                                                         'fixed': "false",
                                                                         'title': "sectionTitle",
                                                                         'visible': "false"})
        assessment_item_ref = SubElement(assessment_section, 'assessmentItemRef', {'identifier': "itemID",
                                                                                   'href': "filename.xml",
                                                                                   'fixed': "false"})
        outcome_processing = SubElement(assessment_test, 'outcomeProcessing')
        set_outcome_value = SubElement(outcome_processing, 'setOutcomeValue', {'identifier': "SCORE"})
        sum_element = SubElement(set_outcome_value, 'sum')
        test_variables = SubElement(sum_element, 'testVariable', {'variableIdentifier': "SCORE"})

        rough_string = tostring(assessment_test)
        reparsed = parseString(rough_string)

        qti_file = open_file(self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()
