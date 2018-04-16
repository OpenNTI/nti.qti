#!/usr/bin/env python
"""
This module contains all the classes that allow for the command-line tool to function properly.

In essence, this module allows for NTI JSON files to be converted into QTI XML files and vice versa.
"""

from argparse import ArgumentParser

from binascii import b2a_hex

from copy import deepcopy

from datetime import datetime

from io import open as open_file

from itertools import product

from json import dumps
from json import loads

from os import listdir
from os import makedirs
from os import remove
from os import urandom

from os.path import basename
from os.path import dirname
from os.path import isdir
from os.path import realpath
from os.path import splitext

from re import compile as compile_pattern
from re import sub
from re import split

from shutil import rmtree

from string import ascii_uppercase

from sys import modules
from sys import exit as sys_exit

from xml.dom.minidom import parseString

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import parse
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring

from zipfile import ZipFile


class Manifest(object):
    """Creates the manifest file for a given QTI file and zips the two files together.

    :param str identifier: The name of the QTI file.
    :param str interaction_type: The question's interaction type.
    :param str path: The path to the QTI file.
    :param str author: The author of the QTI file.
    """
    def __init__(self, identifier, interaction_type, path='', author='author'):
        if isinstance(identifier, str):
            self.identifier = identifier
        else:
            raise TypeError('identifier needs to be a str type')

        if isinstance(interaction_type, str):
            self.interaction_type = interaction_type
        else:
            raise TypeError('interaction_type needs to be a str type')

        if isinstance(path, str):
            self.path = path
        else:
            raise TypeError('path needs to be a str type')

        if isinstance(author, str):
            self.author = author
        else:
            raise TypeError('author needs to be a str type')

        self.manifest()

    def manifest(self):
        """Creates the manifest file for the given QTI XML file."""
        manifest = \
            Element('manifest',
                    {'xmlns': "http://www.imsglobal.org/xsd/imscp_v1p1",
                     'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                     'xsi:schemaLocation':
                         "http://www.imsglobal.org/xsd/imscp_v1p1"
                         "http://www.imsglobal.org/xsd/qti/qtiv2p2/qtiv2p2_imscpv1p2_v1p0.xsd"
                         "http://www.imsglobal.org/xsd/imsqti_v2p2"
                         "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd"
                         "http://www.imsglobal.org/xsd/imsqti_metadata_v2p2"
                         "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_metadata_v2p2.xsd"
                         "http://ltsc.ieee.org/xsd/LOM"
                         "http://www.imsglobal.org/xsd/imsmd_loose_v1p3p2.xsd",
                     'identifier': 'manifestID'})
        metadata = SubElement(manifest, 'metadata')
        schema = SubElement(metadata, 'schema')
        schema.text = 'QTIv2.2 Package'
        schema_version = SubElement(metadata, 'schemaversion')
        schema_version.text = '1.0.0'
        # organizations
        SubElement(manifest, 'organizations')
        resources = SubElement(manifest, 'resources')
        resource = SubElement(resources, 'resource', {'identifier': self.identifier,
                                                      'type': 'imsqti_item_xmlv2p2',
                                                      'href': self.identifier + '.xml'})
        metadata_resource = SubElement(resource, 'metadata')
        lom = SubElement(metadata_resource, 'lom', {'xmls': "http://ltsc.ieee.org/xsd/LOM"})
        general = SubElement(lom, 'general')
        identifier = SubElement(general, 'identifier')
        entry = SubElement(identifier, 'entry')
        entry.text = 'id' + b2a_hex(urandom(16))
        title = SubElement(general, 'title')
        string = SubElement(title, 'string', {'language': "en"})
        string.text = self.identifier
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
        value.text = 'AssessmentItem'
        qti_meta_data = SubElement(lom, 'qtiMetaData',
                                   {'xmlns': "http://www.imsglobal.org/xsd/imsqti_metadata_v2p2"})
        interaction_type = SubElement(qti_meta_data, 'interactionType')
        interaction_type.text = self.interaction_type
        # file
        SubElement(resource, 'file', {'href': self.identifier + '.xml'})

        rough_string = tostring(manifest)
        reparsed = parseString(rough_string)

        if not self.path:
            qti_file = open_file('imsmanifest.xml', 'w+', encoding="utf-8")
        else:
            qti_file = open_file(self.path + 'imsmanifest.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

        self.export()

    def export(self):
        """Zips the generated manifest file and the given QTI XML file together."""
        if not self.path:
            zip_file = ZipFile(self.identifier + '.zip', 'w')
            zip_file.write('imsmanifest.xml')
            remove('imsmanifest.xml')
            zip_file.write(self.identifier + '.xml')
            remove(self.identifier + '.xml')
            zip_file.close()
        else:
            zip_file = ZipFile(self.path + self.identifier + '.zip', 'w')
            zip_file.write(self.path + 'imsmanifest.xml', basename(self.path + 'imsmanifest.xml'))
            remove(self.path + 'imsmanifest.xml')
            zip_file.write(self.path + self.identifier + '.xml',
                           basename(self.path + self.identifier + '.xml'))
            remove(self.path + self.identifier + '.xml')
            zip_file.close()


class ChoiceInteraction(object):
    """Parses the given data into either a QTI XML file or NTI JSON file for Choice Interactions.

    :param str identifier: The question's identifier.
    :param str prompt: The question's prompt.
    :param str title: The file's name and the question's title.
    :param list of str values: The list of correct answers.
    :param list of str choices: The list of possible choices.
    :param str path: The path of the file to be created.
    """
    def __init__(self, identifier, prompt, title, values, choices, path=''):
        if isinstance(identifier, str):
            self.identifier = identifier
        else:
            raise TypeError('identifier needs to be a str type')

        if isinstance(prompt, str):
            self.prompt = prompt
        else:
            raise TypeError('prompt needs to be a str type')

        if isinstance(title, str):
            if not title:
                self.title = identifier
            else:
                self.title = title
        else:
            raise TypeError('title needs to be a str type')

        if isinstance(values, list):
            self.values = values
        else:
            raise TypeError('values[] needs to be a list type')

        if isinstance(choices, list):
            self.choices = choices
        else:
            raise TypeError('choices[] needs to be a list type')

        if isinstance(path, str):
            self.path = path
        else:
            raise TypeError('path needs to be a str type')

        if not identifier:
            raise ValueError('identifier cannot be empty')

        if not prompt:
            raise ValueError('prompt cannot be empty')

        if not isinstance(values[0], str):
            raise TypeError('values[] can only contain str type items')

        if not isinstance(choices[0], str):
            raise TypeError('choices[] can only contain str type items')

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
        """Converts the given data into a QTI XML file.

        :param adaptive: Determines if the question is adaptive or not.
        :param time_dependent: Determines if the question is time-dependent or not.
        :param shuffle: Determines if the question's choices are to be shuffled or not.
        """
        choices = deepcopy(self.choices)
        values = deepcopy(self.values)

        if not choices:
            raise ValueError('choices[] cannot be empty')

        if not values:
            raise ValueError('values[] cannot be empty')

        assessment_item = Element('assessmentItem',
                                  {'xmlns': "http://www.imsglobal.org/xsd/imsqti_v2p2",
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
        choice_interaction = SubElement(item_body, 'choiceInteraction',
                                        {'responseIdentifier': 'RESPONSE',
                                         'shuffle': shuffle,
                                         'maxChoices': '0' if self.multiple_answer else '1'})
        prompt__sub_element = SubElement(choice_interaction, 'prompt')
        prompt__sub_element.text = self.prompt
        identifier = 0
        while choices:
            simple_choice = SubElement(choice_interaction, 'simpleChoice',
                                       {'identifier': str(self.char[str(identifier)])})
            simple_choice.text = choices.pop(0)
            identifier += 1
        # response_processing
        SubElement(assessment_item, 'responseProcessing',
                   {'template':
                    "http://www.imsglobal.org/question/qti_v2p2/rptemplates/match_correct"})

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        if not self.path:
            qti_file = open_file(self.title + '.xml', 'w+', encoding="utf-8")
        else:
            qti_file = open_file(self.path + self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

        if not self.path:
            Manifest(self.title, 'choiceInteraction')
        else:
            Manifest(self.title, 'choiceInteraction', self.path)

    def to_nti(self):
        """Converts the given data into an NTI JSON file."""
        choices = deepcopy(self.choices)
        values = deepcopy(self.values)

        mime_type_q = '"application/vnd.nextthought.naquestion"'
        mime_type_mc = '"application/vnd.nextthought.assessment.multiplechoicepart"'
        mime_type_mc_ma = \
            '"application/vnd.nextthought.assessment.multiplechoicemultipleanswerpart"'
        mime_type_mc_s = '"application/vnd.nextthought.assessment.multiplechoicesolution"'
        mime_type_mc_ma_s = \
            '"application/vnd.nextthought.assessment.multiplechoicemultipleanswersolution"'

        if not choices:
            raise ValueError('choices[] cannot be empty')

        if not values:
            raise ValueError('values[] cannot be empty')

        if not isinstance(int(values[0]), int):
            for place, value in enumerate(values):
                value = str(self.char.keys()[self.char.values().index(values[place])])
                values[place] = value

        nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + \
                   self.identifier + '", "content":"' + self.prompt + '", "ntiid":"' + \
                   self.identifier + '", "parts":[{"Class":' + \
                   ('"MultipleChoiceMultipleAnswerPart"' if self.multiple_answer
                    else '"MultipleChoicePart"') + ', "MimeType":' + \
                   (mime_type_mc_ma if self.multiple_answer else mime_type_mc) + ', "choices":["'
        while choices:
            if len(choices) == 1:
                nti_json += choices.pop(0) + '"], '
            else:
                nti_json += choices.pop(0) + '", "'
        nti_json += '"content":"", "explanation":"", "hints":[], "solutions":[{"Class":' + \
                    ('"MultipleChoiceMultipleAnswerSolution"' if self.multiple_answer
                     else '"MultipleChoiceSolution"') + ', "MimeType":' + \
                    (mime_type_mc_ma_s if self.multiple_answer else mime_type_mc_s) + ', "value":'
        if len(values) == 1:
            nti_json += values.pop(0) + ', '
        else:
            nti_json += '['
            while values:
                if len(values) == 1:
                    nti_json += values.pop(0) + '], '
                else:
                    nti_json += values.pop(0) + ', '
        nti_json += '"weight":1.0}]}]}'

        parsed = loads(nti_json)

        if not self.path:
            nti_file = open_file(self.title + '.json', 'w+', encoding="utf-8")
        else:
            nti_file = open_file(self.path + self.title + '.json', 'w+', encoding="utf-8")
        nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
        nti_file.close()


class ExtendedTextInteraction(object):
    """Parses the given data into either a QTI XML file or NTI JSON file for Extended Text
    Interactions.

    :param str identifier: The question's identifier.
    :param str prompt: The question's prompt.
    :param str title: The file's name and the question's title.
    :param str path: The path of the file to be created.
    """
    def __init__(self, identifier, prompt, title, path=''):
        if isinstance(identifier, str):
            self.identifier = identifier
        else:
            raise TypeError('identifier needs to be a str type')

        if isinstance(prompt, str):
            self.prompt = prompt
        else:
            raise TypeError('prompt needs to be a str type')

        if isinstance(title, str):
            if not title:
                self.title = identifier
            else:
                self.title = title
        else:
            raise TypeError('title needs to be a str type')

        if isinstance(path, str):
            self.path = path
        else:
            raise TypeError('path needs to be a str type')

        if not identifier:
            raise ValueError('identifier cannot be empty')

        if not prompt:
            raise ValueError('prompt cannot be empty')

    def to_qti(self, adaptive='false', time_dependent='false'):
        """Converts the given data into a QTI XML file.

        :param adaptive: Determines if the question is adaptive or not.
        :param time_dependent: Determines if the question is time-dependent or not.
        """
        assessment_item = Element('assessmentItem',
                                  {'xmlns': "http://www.imsglobal.org/xsd/imsqti_v2p2",
                                   'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                   'xsi:schemaLocation':
                                       "http://www.imsglobal.org/xsd/imsqti_v2p2 "
                                       "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd",
                                   'identifier': self.identifier,
                                   'title': self.title,
                                   'adaptive': adaptive,
                                   'timeDependent': time_dependent})
        # response_declaration
        SubElement(assessment_item, 'responseDeclaration', {'identifier': 'RESPONSE',
                                                            'cardinality': 'single',
                                                            'baseType': 'string'})
        # outcome_declaration
        SubElement(assessment_item, 'outcomeDeclaration', {'identifier': 'SCORE',
                                                           'cardinality': 'single',
                                                           'baseType': 'float'})
        item_body = SubElement(assessment_item, 'itemBody')
        extended_text_interaction = SubElement(item_body, 'extendedTextInteraction',
                                               {'responseIdentifier': 'RESPONSE'})
        prompt__sub_element = SubElement(extended_text_interaction, 'prompt')
        prompt__sub_element.text = self.prompt

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        if not self.path:
            qti_file = open_file(self.title + '.xml', 'w+', encoding="utf-8")
        else:
            qti_file = open_file(self.path + self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

        if not self.path:
            Manifest(self.title, 'extendedTextInteraction')
        else:
            Manifest(self.title, 'extendedTextInteraction', self.path)

    def to_nti(self):
        """Converts the given data into an NTI JSON file."""
        mime_type_q = '"application/vnd.nextthought.naquestion"'
        mime_type_model = '"application/vnd.nextthought.assessment.modeledcontentpart"'

        nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + \
                   self.identifier + '", "content":"' + self.prompt + '", "ntiid":"' + \
                   self.identifier + '", "parts":[{"Class":"ModeledContentPart", "MimeType":' + \
                   mime_type_model + ', "content":"", "explanation":"", "hints":[], ' \
                   '"solutions":[]}]}'

        parsed = loads(nti_json)

        if not self.path:
            nti_file = open_file(self.title + '.json', 'w+', encoding="utf-8")
        else:
            nti_file = open_file(self.path + self.title + '.json', 'w+', encoding="utf-8")
        nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
        nti_file.close()


class InlineChoiceInteraction(object):
    """Parses the given data into either a QTI XML file or NTI JSON file for Inline Choice
    Interactions.

    :param str identifier: The question's identifier.
    :param str prompt: The question's prompt.
    :param str title: The file's name and the question's title.
    :param list of str labels: The list of labels for solutions.
    :param list of str solutions: The list of correct answers.
    :param list of Word wordbank: The list of words to pick from.
    :param str path: The path of the file to be created.
    """
    def __init__(self, identifier, prompt, title, labels, solutions, wordbank, path=''):
        if isinstance(identifier, str):
            self.identifier = identifier
        else:
            raise TypeError('identifier needs to be a str type')

        if isinstance(prompt, str):
            self.prompt = prompt
        else:
            raise TypeError('prompt needs to be a str type')

        if isinstance(title, str):
            if not title:
                self.title = identifier
            else:
                self.title = title
        else:
            raise TypeError('title needs to be a str type')

        if isinstance(labels, list):
            self.labels = labels
        else:
            raise TypeError('labels[] needs to be a list type')

        if isinstance(solutions, list):
            self.solutions = solutions
        else:
            raise TypeError('solutions[] needs to be a list type')

        if isinstance(wordbank, list):
            self.wordbank = wordbank
        else:
            raise TypeError('wordbank[] needs to be a list type')

        if isinstance(path, str):
            self.path = path
        else:
            raise TypeError('path needs to be a str type')

        if not identifier:
            raise ValueError('identifier cannot be empty')

        if not prompt:
            raise ValueError('prompt cannot be empty')

        if not labels:
            raise ValueError('labels[] cannot be empty')

        if not solutions:
            raise ValueError('solutions[] cannot be empty')

        if not wordbank:
            raise ValueError('wordbank[] cannot be empty')

        if len(labels) != len(solutions):
            raise ValueError('labels[] must have the same length as solutions[]')

        self.content = ''
        self.input = ''

        self.char = self.dictionary(1)
        self.double_char = self.dictionary(2)

    def to_qti(self, adaptive='false', time_dependent='false', shuffle='false'):
        """Converts the given data into a QTI XML file.

        :param adaptive: Determines if the question is adaptive or not.
        :param time_dependent: Determines if the question is time-dependent or not.
        :param shuffle: Determines if the question's choices are to be shuffled or not.
        """
        labels = deepcopy(self.labels)
        solutions = deepcopy(self.solutions)
        wordbank = deepcopy(self.wordbank)

        if not labels:
            raise ValueError('labels[] cannot be empty')

        if not solutions:
            raise ValueError('solutions[] cannot be empty')

        if not wordbank:
            raise ValueError('wordbank[] cannot be empty')

        prompt_pattern = compile_pattern('<input type=\\\\"blankfield\\\\" name=\\\\"\d{3}\\\\" />')
        mod_prompt = split(prompt_pattern, self.prompt)

        assessment_item = Element('assessmentItem',
                                  {'xmlns': "http://www.imsglobal.org/xsd/imsqti_v2p2",
                                   'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                   'xsi:schemaLocation':
                                       "http://www.imsglobal.org/xsd/imsqti_v2p2 "
                                       "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd",
                                   'identifier': self.identifier,
                                   'title': self.title,
                                   'adaptive': adaptive,
                                   'timeDependent': time_dependent})
        for item in range(len(self.labels)):
            response_declaration = SubElement(assessment_item, 'responseDeclaration', {
                'identifier': 'RESPONSE' + str(labels[item]), 'cardinality': 'single', 'baseType':
                    'identifier'
            })
            correct_response = SubElement(response_declaration, 'correctResponse')
            value = SubElement(correct_response, 'value')
            value.text = self.char[solutions[item]]
            mapping = SubElement(response_declaration, 'mapping')
            for num in range(len(self.labels)):
                if self.char[solutions[item]] == self.char[solutions[num]]:
                    # map_entry
                    SubElement(mapping, 'mapEntry', {
                        'mapKey': self.char[solutions[num]], 'mappedValue': '1'})
                else:
                    # map_entry
                    SubElement(mapping, 'mapEntry', {
                        'mapKey': self.char[solutions[num]], 'mappedValue': '0'})
        # outcome_declaration
        SubElement(assessment_item, 'outcomeDeclaration', {'identifier': 'SCORE',
                                                           'cardinality': 'single',
                                                           'baseType': 'float'})
        item_body = SubElement(assessment_item, 'itemBody')
        prompt = SubElement(item_body, 'p')
        prompt.text = mod_prompt.pop(0)
        while labels:
            inline_choice_interaction = SubElement(prompt, 'inlineChoiceInteraction', {
                'responseIdentifier': 'RESPONSE' + str(labels.pop(0)), 'shuffle': shuffle
            })
            for num in range(len(wordbank)):
                inline_choice = SubElement(inline_choice_interaction, 'inlineChoice', {
                    'identifier': self.char[wordbank[num].wid]
                })
                inline_choice.text = wordbank[num].content
            inline_choice_interaction.tail = mod_prompt.pop(0)
        # response_processing
        SubElement(assessment_item, 'responseProcessing',
                   {'template':
                    "http://www.imsglobal.org/question/qti_v2p2/rptemplates/map_response"})

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        if not self.path:
            qti_file = open_file(self.title + '.xml', 'w+', encoding="utf-8")
        else:
            qti_file = open_file(self.path + self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

        if not self.path:
            Manifest(self.title, 'inlineChoiceInteraction')
        else:
            Manifest(self.title, 'inlineChoiceInteraction', self.path)

    def to_nti(self):
        """Converts the given data into an NTI JSON file."""
        labels = deepcopy(self.labels)
        solutions = deepcopy(self.solutions)
        wordbank = deepcopy(self.wordbank)

        mime_type_q = '"application/vnd.nextthought.naquestionfillintheblankwordbank"'
        mime_type_b = '"application/vnd.nextthought.assessment.fillintheblankwithwordbankpart"'
        mime_type_b_s = \
            '"application/vnd.nextthought.assessment.fillintheblankwithwordbanksolution"'
        mime_type_w = '"application/vnd.nextthought.naqwordbank"'
        mime_type_we = '"application/vnd.nextthought.naqwordentry"'

        if compile_pattern('<a.*></a> ').match(self.prompt) is not None:
            self.input = sub('<a.*></a> ', '', self.prompt)
            prompt_mod = compile_pattern('(<a.*></a>).*').match(self.prompt).group(1)
        else:
            prompt_mod = self.prompt

        if not labels:
            raise ValueError('labels[] cannot be empty')

        if not solutions:
            raise ValueError('solutions[] cannot be empty')

        if not wordbank:
            raise ValueError('wordbank[] cannot be empty')

        nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + \
                   self.identifier + '", "content":"' + prompt_mod + '", "ntiid":"' + \
                   self.identifier + '", "parts":[{"Class":"FillInTheBlankWithWordBankPart", ' \
                   '"MimeType":' + mime_type_b + ', "content":"", "explanation":"", "hints":[], ' \
                   '"input":"' + self.input + '", "solutions":[{"Class":' \
                   '"FillInTheBlankWithWordBankSolution", "MimeType":' + mime_type_b_s + \
                   ', "value":{'
        while labels:
            nti_json += '"' + labels.pop(0) + '":["' + solutions.pop(0) + '"]'
            if len(labels) != 0:
                nti_json += ','
        nti_json += '}, "weight":1.0}], "wordbank":{"Class":"WordBank", "MimeType":' + mime_type_w \
                    + ', "entries":['
        while wordbank:
            nti_json += '{"Class":"WordEntry", "MimeType":' + mime_type_we + ', "content":"' + \
                        wordbank[0].content + '", "lang":"en", "wid":"' + wordbank[0].wid + '", ' \
                        '"word":"' + wordbank.pop(0).content + '"}'
            if len(wordbank) >= 1:
                nti_json += ','
        nti_json += '], "unique":true}}], "wordbank":null}'

        parsed = loads(nti_json)

        if not self.path:
            nti_file = open_file(self.title + '.json', 'w+', encoding="utf-8")
        else:
            nti_file = open_file(self.path + self.title + '.json', 'w+', encoding="utf-8")
        nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
        nti_file.close()

    @staticmethod
    def dictionary(size):
        """Creates a dictionary of given size where {'0':'A', '1':'B', ..., 'n':'...Z'} ."""
        if size < 1:
            raise ValueError('size must be greater than 0')
        pre_dict = []
        for char in product(ascii_uppercase, repeat=size):
            pre_dict.append("".join(char))
        return dict(zip(map(str, range(26 ** size)), pre_dict))


class MatchInteraction(object):
    """Parses the given data into either a QTI XML file or NTI JSON file for Match Interactions.

    :param str identifier: The question's identifier.
    :param str prompt: The question's prompt.
    :param str title: The file's name and the question's title.
    :param list of str labels: The list of labels to be matched from.
    :param list of str solutions: The list of correct answers.
    :param list of str values: The list of values to be matched to.
    :param str path: The path of the file to be created.
    """
    def __init__(self, identifier, prompt, title, labels, solutions, values, path=''):
        if isinstance(identifier, str):
            self.identifier = identifier
        else:
            raise TypeError('identifier needs to be a str type')

        if isinstance(prompt, str):
            self.prompt = prompt
        else:
            raise TypeError('prompt needs to be a str type')

        if isinstance(title, str):
            if not title:
                self.title = identifier
            else:
                self.title = title
        else:
            raise TypeError('title needs to be a str type')

        if isinstance(labels, list):
            self.labels = labels
        else:
            raise TypeError('labels[] needs to be a list type')

        if isinstance(solutions, list):
            self.solutions = solutions
        else:
            raise TypeError('solutions[] needs to be a list type')

        if isinstance(values, list):
            self.values = values
        else:
            raise TypeError('values[] needs to be a list type')

        if isinstance(path, str):
            self.path = path
        else:
            raise TypeError('path needs to be a str type')

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

        if len(labels) != len(values):
            raise ValueError('labels[] must have the same length as values[]')

        self.solution_pattern = compile_pattern('(.+) (.+)')

        self.char = self.dictionary(1)
        self.double_char = self.dictionary(2)

    def to_qti(self, adaptive='false', time_dependent='false', shuffle='false'):
        """Converts the given data into a QTI XML file.

        :param adaptive: Determines if the question is adaptive or not.
        :param time_dependent: Determines if the question is time-dependent or not.
        :param shuffle: Determines if the question's choices are to be shuffled or not.
        """
        labels = deepcopy(self.labels)
        solutions = deepcopy(self.solutions)
        values = deepcopy(self.values)

        if not labels:
            raise ValueError('labels[] cannot be empty')

        if not solutions:
            raise ValueError('solutions[] cannot be empty')

        if not values:
            raise ValueError('values[] cannot be empty')

        assessment_item = Element('assessmentItem',
                                  {'xmlns': "http://www.imsglobal.org/xsd/imsqti_v2p2",
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
            correct_response_value.text = str(self.char[str(matcher.group(1))] + ' ' +
                                              self.double_char[str(matcher.group(2))])
            solutions.pop(0)
        # outcome_declaration
        SubElement(assessment_item, 'outcomeDeclaration', {'identifier': 'SCORE',
                                                           'cardinality': 'single',
                                                           'baseType': 'float'})
        item_body = SubElement(assessment_item, 'itemBody')
        match_interaction = SubElement(item_body, 'matchInteraction', {'responseIdentifier':
                                                                       'RESPONSE',
                                                                       'shuffle': shuffle,
                                                                       'maxAssociations': '0'})
        prompt__sub_element = SubElement(match_interaction, 'prompt')
        prompt__sub_element.text = self.prompt
        simple_match_set_1 = SubElement(match_interaction, 'simpleMatchSet')
        identifier = 0
        while labels:
            simple_associable_choice = SubElement(simple_match_set_1, 'simpleAssociableChoice',
                                                  {'identifier': self.char[str(identifier)],
                                                   'matchMax': '1'})
            simple_associable_choice.text = labels.pop(0)
            identifier += 1
        simple_match_set_2 = SubElement(match_interaction, 'simpleMatchSet')
        identifier = 0
        while values:
            simple_associable_choice = SubElement(simple_match_set_2, 'simpleAssociableChoice',
                                                  {'identifier': self.double_char[str(identifier)],
                                                   'matchMax': '1'})
            simple_associable_choice.text = values.pop(0)
            identifier += 1
        # response_processing
        SubElement(assessment_item, 'responseProcessing',
                   {'template':
                    "http://www.imsglobal.org/question/qti_v2p2/rptemplates/match_correct"})

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        if not self.path:
            qti_file = open_file(self.title + '.xml', 'w+', encoding="utf-8")
        else:
            qti_file = open_file(self.path + self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

        if not self.path:
            Manifest(self.title, 'matchInteraction')
        else:
            Manifest(self.title, 'matchInteraction', self.path)

    def to_nti(self):
        """Converts the given data into an NTI JSON file."""
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

        nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + \
                   self.identifier + '", "content":"' + self.prompt + '", "ntiid":"' + \
                   self.identifier + '", "parts":[{"Class":"MatchingPart", "MimeType":' + \
                   mime_type_ma + ', "content":"", "explanation":"", "hints":[], "labels":["'
        while labels:
            if len(labels) == 1:
                nti_json += labels.pop(0) + '"], '
            else:
                nti_json += labels.pop(0) + '", "'
        nti_json += \
            '"solutions":[{"Class":"MatchingSolution", "MimeType":' + mime_type_ma_s + ', "value":{'
        while solutions:
            matcher = self.solution_pattern.search(solutions[0])
            if len(solutions) == 1:
                nti_json += '"' + matcher.group(1) + '":' + matcher.group(2) + '}, '
            else:
                nti_json += '"' + matcher.group(1) + '":' + matcher.group(2) + ', '
            solutions.pop(0)
        nti_json += '"weight":1.0}], "values":["'
        while values:
            if len(values) == 1:
                nti_json += values.pop(0) + '"]}]}'
            else:
                nti_json += values.pop(0) + '", "'

        parsed = loads(nti_json)

        if not self.path:
            nti_file = open_file(self.title + '.json', 'w+', encoding="utf-8")
        else:
            nti_file = open_file(self.path + self.title + '.json', 'w+', encoding="utf-8")
        nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
        nti_file.close()

    @staticmethod
    def dictionary(size):
        """Creates a dictionary of given size where {'0':'A', '1':'B', ..., 'n':'...Z'} ."""
        if size < 1:
            raise ValueError('size must be greater than 0')
        pre_dict = []
        for char in product(ascii_uppercase, repeat=size):
            pre_dict.append("".join(char))
        return dict(zip(map(str, range(26 ** size)), pre_dict))


class TextEntryInteraction(object):
    """Parses the given data into either a QTI XML file or NTI JSON file for Text Entry
    Interactions.

    :param str identifier: The question's identifier.
    :param str prompt: The question's prompt.
    :param str title: The file's name and the question's title.
    :param list of str or str values: The list of correct answers.
    :param bool math: Distinguishes math-based interactions from non-math-based ones.
    :param str path: The path of the file to be created.
    """
    def __init__(self, identifier, prompt, title, values, math=False, path=''):
        if isinstance(identifier, str):
            self.identifier = identifier
        else:
            raise TypeError('identifier needs to be a str type')

        if isinstance(prompt, str):
            self.prompt = prompt
        else:
            raise TypeError('prompt needs to be a str type')

        if isinstance(title, str):
            if not title:
                self.title = identifier
            else:
                self.title = title
        else:
            raise TypeError('title needs to be a str type')

        if isinstance(math, bool):
            self.math = math
        else:
            raise TypeError('math needs to be a bool type')

        if not self.math:
            if isinstance(values, list):
                self.values = values
            else:
                raise TypeError('values[] needs to be a list type')
        if self.math:
            if isinstance(values, str):
                self.values = values
            else:
                raise TypeError('values needs to be a str type')

        if isinstance(path, str):
            self.path = path
        else:
            raise TypeError('path needs to be a str type')

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

        if not self.math:
            if not isinstance(values[0], str):
                raise TypeError('values[] can only contain str type items')

        if self.math:
            self.content = ''

    def to_qti(self, adaptive='false', time_dependent='false'):
        """Converts the given data into a QTI XML file.

        :param adaptive: Determines if the question is adaptive or not.
        :param time_dependent: Determines if the question is time-dependent or not.
        """
        length = str(len(self.values))
        new_prompt = split('_+', self.prompt)
        values = deepcopy(self.values)

        if not self.math:
            length = str(self.prompt.count('_'))

        assessment_item = Element('assessmentItem',
                                  {'xmlns': "http://www.imsglobal.org/xsd/imsqti_v2p2",
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
        prompt = SubElement(item_body, 'p')
        if not self.math:
            prompt.text = new_prompt.pop(0)
        if self.math:
            prompt.text = self.prompt
        text_entry_interaction = SubElement(prompt, 'textEntryInteraction',
                                            {'responseIdentifier': 'RESPONSE',
                                             'expectedLength': length})
        if not self.math and new_prompt:
            text_entry_interaction.tail = new_prompt.pop(0)
        if not self.math:
            # response_processing
            SubElement(assessment_item, 'responseProcessing',
                       {'template':
                        'http://www.imsglobal.org/question/qti_v2p2/rptemplates/map_response'})
        if self.math:
            # response_processing
            SubElement(assessment_item, 'responseProcessing',
                       {'template':
                        'http://www.imsglobal.org/question/qti_v2p2/rptemplates/match_correct'})

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        if not self.path:
            qti_file = open_file(self.title + '.xml', 'w+', encoding="utf-8")
        else:
            qti_file = open_file(self.path + self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

        if not self.path:
            Manifest(self.title, 'textEntryInteraction')
        else:
            Manifest(self.title, 'textEntryInteraction', self.path)

    def to_nti(self):
        """Converts the given data into an NTI JSON file."""
        if not self.math:
            values = deepcopy(self.values)

            mime_type_q = '"application/vnd.nextthought.naquestion"'
            mime_type_f = '"application/vnd.nextthought.assessment.freeresponsepart"'
            mime_type_f_s = '"application/vnd.nextthought.assessment.freeresponsesolution"'

            nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + \
                       self.identifier + '", "content":"' + self.prompt + '", "ntiid":"' + \
                       self.identifier + '", "parts":[{"Class":"FreeResponsePart", "MimeType":' + \
                       mime_type_f + ', "content":"", "explanation":"", "hints":[], "solutions":['
            while values:
                if len(values) == 1:
                    nti_json += '{"Class":"FreeResponseSolution", "MimeType":' + mime_type_f_s + \
                                ', "value":"' + values.pop(0) + '", "weight":1.0}]}]}'
                else:
                    nti_json += '{"Class":"FreeResponseSolution", "MimeType":' + mime_type_f_s + \
                                ', "value":"' + values.pop(0) + '", "weight":1.0},'

            parsed = loads(nti_json)

            if not self.path:
                nti_file = open_file(self.title + '.json', 'w+', encoding="utf-8")
            else:
                nti_file = open_file(self.path + self.title + '.json', 'w+', encoding="utf-8")
            nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
            nti_file.close()

        if self.math:
            mime_type_q = '"application/vnd.nextthought.naquestion"'
            mime_type_s_m = '"application/vnd.nextthought.assessment.symbolicmathpart"'
            mime_type_s_m_s = '"application/vnd.nextthought.assessment.latexsymbolicmathsolution"'

            if compile_pattern('<a.*></a> ').match(self.prompt) is not None:
                self.content = sub('<a.*></a> ', '', self.prompt)
                self.prompt = compile_pattern('(<a.*></a>).*').match(self.prompt).group(1)

            nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + \
                       self.identifier + '", "content":"' + self.prompt + '", "ntiid":"' + \
                       self.identifier + '", "parts":[{"Class":"SymbolicMathPart", "MimeType":' + \
                       mime_type_s_m + ', "allowed_units":[""], "content":"' + self.content + \
                       '","explanation":"", "hints":[], "solutions":[{"Class":' \
                       '"LatexSymbolicMathSolution", "MimeType":' + mime_type_s_m_s + ', ' \
                       '"allowed_units":[""], "value":"' + self.values + '", "weight":1.0}]}]}'

            parsed = loads(nti_json)

            if not self.path:
                nti_file = open_file(self.title + '.json', 'w+', encoding="utf-8")
            else:
                nti_file = open_file(self.path + self.title + '.json', 'w+', encoding="utf-8")
            nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
            nti_file.close()


class UploadInteraction(object):
    """Parses the given data into either a QTI XML file or NTI JSON file for Choice Interactions.

    :param str identifier: The question's identifier.
    :param str prompt: The question's prompt.
    :param str title: The file's name and the question's title.
    :param str path: The path of the file to be created.
    """
    def __init__(self, identifier, prompt, title, path=''):
        if isinstance(identifier, str):
            self.identifier = identifier
        else:
            raise TypeError('identifier needs to be a str type')

        if isinstance(prompt, str):
            self.prompt = prompt
        else:
            raise TypeError('prompt needs to be a str type')

        if isinstance(title, str):
            if not title:
                self.title = identifier
            else:
                self.title = title
        else:
            raise TypeError('title needs to be a str type')

        if isinstance(path, str):
            self.path = path
        else:
            raise TypeError('path needs to be a str type')

        if not identifier:
            raise ValueError('identifier cannot be empty')

        if not prompt:
            raise ValueError('prompt cannot be empty')

    def to_qti(self, adaptive='false', time_dependent='false'):
        """Converts the given data into a QTI XML file.

        :param adaptive: Determines if the question is adaptive or not.
        :param time_dependent: Determines if the question is time-dependent or not.
        """
        assessment_item = Element('assessmentItem',
                                  {'xmlns': "http://www.imsglobal.org/xsd/imsqti_v2p2",
                                   'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                                   'xsi:schemaLocation':
                                       "http://www.imsglobal.org/xsd/imsqti_v2p2 "
                                       "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd",
                                   'identifier': self.identifier,
                                   'title': self.title,
                                   'adaptive': adaptive,
                                   'timeDependent': time_dependent})
        # response_declaration
        SubElement(assessment_item, 'responseDeclaration', {'identifier': 'RESPONSE',
                                                            'cardinality': 'single',
                                                            'baseType': 'file'})
        # outcome_declaration
        SubElement(assessment_item, 'outcomeDeclaration', {'identifier': 'SCORE',
                                                           'cardinality': 'single',
                                                           'baseType': 'float'})
        item_body = SubElement(assessment_item, 'itemBody')
        upload_interaction = SubElement(item_body, 'uploadInteraction', {'responseIdentifier':
                                                                         'RESPONSE'})
        prompt__sub_element = SubElement(upload_interaction, 'prompt')
        prompt__sub_element.text = self.prompt

        rough_string = tostring(assessment_item)
        reparsed = parseString(rough_string)

        if not self.path:
            qti_file = open_file(self.title + '.xml', 'w+', encoding="utf-8")
        else:
            qti_file = open_file(self.path + self.title + '.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

        if not self.path:
            Manifest(self.title, 'uploadInteraction')
        else:
            Manifest(self.title, 'uploadInteraction', self.path)

    def to_nti(self):
        """Converts the given data into an NTI JSON file."""
        mime_type_q = '"application/vnd.nextthought.naquestion"'
        mime_type_f = '"application/vnd.nextthought.assessment.filepart"'

        nti_json = '{"Class":"Question", "MimeType":' + mime_type_q + ', "NTIID":"' + \
                   self.identifier + '", "content":"' + self.prompt + '", "ntiid":"' + \
                   self.identifier + '", "parts":[{"Class":"FilePart", "MimeType":' + \
                   mime_type_f + ', "allowed_extensions":[".docx", ".pdf"], ' \
                   '"allowed_mime_types":["*/*"], "content":"", "explanation":"", "hints":[], ' \
                   '"max_file_size":10485760, "solutions":[]}]}'

        parsed = loads(nti_json)

        if not self.path:
            nti_file = open_file(self.title + '.json', 'w+', encoding="utf-8")
        else:
            nti_file = open_file(self.path + self.title + '.json', 'w+', encoding="utf-8")
        nti_file.write(unicode(dumps(parsed, indent=4, sort_keys=True)))
        nti_file.close()


class NTICollector(object):
    """Traverses a given NTI JSON file and collects data so that it can be converted.

    :param str file_name: The file's name.
    :param str path: The path of the file to be created.
    """
    def __init__(self, file_name, path='', class_type=''):
        if isinstance(path, str):
            if path:
                try:
                    makedirs(path)
                except OSError:
                    if not isdir(path):
                        raise
            self.path = path
        else:
            raise TypeError('path needs to be a str type')

        if isinstance(file_name, str):
            if path:
                self.file_name = \
                    compile_pattern('([\\/].*[\\/]).*[\\/]').search(path).group(1) + file_name
            else:
                self.file_name = file_name
        else:
            raise TypeError('file_name needs to be a str type')

        if not file_name.lower().endswith('.json'):
            raise TypeError('file_name must be a .json file')

        self.line_counter = 0
        self.total_lines = sum(1 for line in open(self.file_name) if line.rstrip())

        self.class_type = ''
        self.content = ''
        self.identifier = ''
        self.prompt = ''
        self.title = ''
        self.wid = ''
        self.word = ''
        self.value_single = ''

        self.choices = []
        self.labels = []
        self.questions = []
        self.solutions = []
        self.words = []
        self.values = []

        self.types = ('AssignmentPart', 'FilePart', 'FillInTheBlankWithWordBankPart',
                      'FreeResponsePart', 'MatchingPart', 'ModeledContentPart',
                      'MultipleChoicePart', 'MultipleChoiceMultipleAnswerPart', 'OrderingPart',
                      'SymbolicMathPart')

        self.collect()
        self.convert(class_type)

    def collect(self):
        """Collects data from source NTI JSON file and converts files along the way."""
        infile = open(self.file_name, 'r')
        for line in infile:
            self.line_counter += 1

            if '"Class": "Poll",' in line:
                while '"Class": "Question"' not in line:
                    self.line_counter += 1
                    line = next(infile)

            if ('"NTIID":' or '"ntiid":') in line:
                matcher = \
                    compile_pattern(r'"(NTIID|ntiid)": '
                                    r'"(tag:.+_(.+)\.naq\.qid(\.content)?(\..+))",?').search(line)
                if matcher is not None:
                    self.identifier = str(matcher.group(2))
                    self.title = str(matcher.group(3)) + str(matcher.group(5))

            if '"content":' in line:
                matcher = compile_pattern('"content": "(.*)",?').search(line)
                if matcher is not None:
                    self.prompt = matcher.group(1)

            if '"Class": "FilePart"' in line:
                self.questions.append(UploadInteraction(self.identifier, self.prompt, self.title,
                                                        self.path))

            if '"Class": "FillInTheBlankWithWordBankPart",' in line:
                while ('"Class": "Question"' not in line and '"Class": "Poll"' not in line) and \
                        not self.line_counter == self.total_lines:
                    self.line_counter += 1
                    line = next(infile)

                    if '"content": "",' in line:
                        self.line_counter += 1
                        line = next(infile)
                    elif '"content":' in line:
                        matcher = compile_pattern('"content": "(.*)",?').search(line)
                        if matcher is not None:
                            self.prompt += ' ' + matcher.group(1)

                    if '"input": "",' in line:
                        self.line_counter += 1
                        line = next(infile)
                    elif '"input":' in line:
                        matcher = compile_pattern('"input": "(.+)",?').search(line)
                        if matcher is not None:
                            self.prompt += ' ' + matcher.group(1)

                    if '"value": {' in line:
                        while '}' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = compile_pattern('"(\\d{3})": \\[').search(line)
                            if matcher is not None:
                                self.labels.append(str(matcher.group(1)))

                            matcher = compile_pattern('"(\\d{1,3})"(?!:)').search(line)
                            if matcher is not None:
                                self.solutions.append(str(matcher.group(1)))

                    if '"entries": [' in line:
                        while ']' not in line:
                            self.line_counter += 1
                            line = next(infile)
                            matcher = compile_pattern('"content": "(.*)",?').search(line)
                            if matcher is not None:
                                self.content = str(matcher.group(1))
                            matcher = compile_pattern('"wid": "(.*)",?').search(line)
                            if matcher is not None:
                                self.wid = str(matcher.group(1))
                            matcher = compile_pattern('"word": "(.*)",?').search(line)
                            if matcher is not None:
                                self.word = str(matcher.group(1))

                            if self.content and self.wid:
                                self.words.append(self.Word(self.content, self.wid))
                                self.content = ''
                                self.wid = ''
                            elif self.word and self.wid:
                                self.words.append(self.Word(self.word, self.wid))
                                self.content = ''
                                self.wid = ''

                self.questions.append(InlineChoiceInteraction(self.identifier, self.prompt,
                                                              self.title, self.labels,
                                                              self.solutions, self.words,
                                                              self.path))

                self.labels = []
                self.solutions = []
                self.words = []

                if '"Class": "Poll",' in line:
                    while '"Class": "Question"' not in line:
                        self.line_counter += 1
                        line = next(infile)

            if '"Class": "FreeResponsePart",' in line:
                while ('"Class": "Question"' not in line and '"Class": "Poll"' not in line) and \
                        not self.line_counter == self.total_lines:
                    self.line_counter += 1
                    line = next(infile)

                    if '"value": ' in line:
                        matcher = compile_pattern('"value": "(.+)",?').search(line)
                        if matcher is not None:
                            self.values.append(str(matcher.group(1)))

                    if '"content": "",' in line:
                        self.line_counter += 1
                        line = next(infile)
                    elif '"content":' in line:
                        matcher = compile_pattern('"content": "(.*)",?').search(line)
                        if matcher is not None:
                            self.prompt += ' ' + matcher.group(1)

                self.questions.append(
                    TextEntryInteraction(self.identifier, self.prompt, self.title, self.values,
                                         False, self.path))

                self.choices = []
                self.values = []

                if '"Class": "Poll",' in line:
                    while '"Class": "Question"' not in line:
                        self.line_counter += 1
                        line = next(infile)

            if '"Class": "MatchingPart"' in line or '"Class": "OrderingPart"' in line:
                matcher = compile_pattern('"Class": "(.+Part)",?').search(line)
                if matcher is not None:
                    self.class_type = matcher.group(1)
                while ('"Class": "Question"' not in line and '"Class": "Poll"' not in line) and \
                        not self.line_counter == self.total_lines:
                    self.line_counter += 1
                    line = next(infile)

                    if '"content": "",' in line:
                        self.line_counter += 1
                        line = next(infile)
                    elif '"content":' in line:
                        matcher = compile_pattern('"content": "(.*)",?').search(line)
                        if matcher is not None:
                            self.prompt += ' ' + matcher.group(1)

                    if '"labels": [' in line:
                        while ']' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = compile_pattern('"(.+)",?').search(line)
                            if matcher is not None:
                                self.labels.append(str(matcher.group(1)))

                    if '"value": {' in line:
                        while '}' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = compile_pattern('"(\\d+)":( \\d+),?').search(line)
                            if matcher is not None:
                                self.solutions.append(str(matcher.group(1) + matcher.group(2)))

                    if '"values": [' in line:
                        while ']' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = compile_pattern('"(.+)",?').search(line)
                            if matcher is not None:
                                self.values.append(str(matcher.group(1)))

                if self.class_type == 'MatchingPart':
                    self.questions.append(
                        MatchInteraction(self.identifier, self.prompt, self.title, self.labels,
                                         self.solutions, self.values, self.path))

                elif self.class_type == 'OrderingPart':
                    self.questions.append(
                        MatchInteraction(self.identifier, self.prompt, self.title, self.labels,
                                         self.solutions, self.values, self.path))

                self.labels = []
                self.values = []
                self.solutions = []

                if '"Class": "Poll",' in line:
                    while '"Class": "Question"' not in line:
                        self.line_counter += 1
                        line = next(infile)

            if '"Class": "ModeledContentPart"' in line:
                self.questions.append(ExtendedTextInteraction(self.identifier, self.prompt,
                                                              self.title, self.path))

            if '"Class": "MultipleChoicePart",' in line:
                while ('"Class": "Question"' not in line and '"Class": "Poll"' not in line) and \
                        not self.line_counter == self.total_lines:
                    self.line_counter += 1
                    line = next(infile)

                    if '"choices": [' in line:
                        while '],' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = \
                                compile_pattern('"(<a name=.+>.*</a>.*<p class=.+id=.+>(.+)</p>)"')\
                                .search(line)
                            if matcher is not None:
                                self.choices.append(matcher.group(1))

                    if '"content": "",' in line:
                        self.line_counter += 1
                        line = next(infile)
                    elif '"content":' in line:
                        matcher = compile_pattern('"content": "(.*)",?').search(line)
                        if matcher is not None:
                            self.prompt += ' ' + matcher.group(1)

                    if '"value":' in line:
                        matcher = compile_pattern('"value": (\\d),?').search(line)
                        if matcher is not None:
                            self.values.append(matcher.group(1))

                self.questions.append(ChoiceInteraction(self.identifier, self.prompt, self.title,
                                                        self.values, self.choices, self.path))

                self.choices = []
                self.values = []

                if '"Class": "Poll",' in line:
                    while '"Class": "Question"' not in line:
                        self.line_counter += 1
                        line = next(infile)

            if '"Class": "MultipleChoiceMultipleAnswerPart",' in line:
                while ('"Class": "Question"' not in line and '"Class": "Poll"' not in line) and \
                        not self.line_counter == self.total_lines:
                    self.line_counter += 1
                    line = next(infile)

                    if '"choices": [' in line:
                        while '],' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = \
                                compile_pattern('"(<a name=.+>.*</a>.*<p class=.+id=.+>(.+)</p>)"')\
                                .search(line)
                            if matcher is not None:
                                self.choices.append(matcher.group(1))

                    if '"content": "",' in line:
                        self.line_counter += 1
                        line = next(infile)
                    elif '"content":' in line:
                        matcher = compile_pattern('"content": "(.*)",?').search(line)
                        if matcher is not None:
                            self.prompt += ' ' + matcher.group(1)

                    if '"value": [' in line:
                        while '],' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = compile_pattern('(\\d),?').search(line)
                            if matcher is not None:
                                self.values.append(matcher.group(1))

                self.questions.append(ChoiceInteraction(self.identifier, self.prompt, self.title,
                                                        self.values, self.choices, self.path))

                self.choices = []
                self.values = []

                if '"Class": "Poll",' in line:
                    while '"Class": "Question"' not in line:
                        self.line_counter += 1
                        line = next(infile)

            if '"Class": "SymbolicMathPart",' in line:
                while ('"Class": "Question"' not in line and '"Class": "Poll"' not in line) and \
                        not self.line_counter == self.total_lines:
                    self.line_counter += 1
                    line = next(infile)

                    if '"content": "",' in line:
                        self.line_counter += 1
                        line = next(infile)
                    elif '"content":' in line:
                        matcher = compile_pattern('"content": "(.*)",?').search(line)
                        if matcher is not None:
                            self.prompt += ' ' + matcher.group(1)

                    if '"value": ' in line:
                        matcher = compile_pattern('"value": "(.+)",?').search(line)
                        if matcher is not None:
                            self.value_single = str(matcher.group(1))

                self.questions.append(
                    TextEntryInteraction(self.identifier, self.prompt, self.title,
                                         self.value_single, True, self.path))

                self.choices = []
                self.values = []

                if '"Class": "Poll",' in line:
                    while '"Class": "Question"' not in line:
                        self.line_counter += 1
                        line = next(infile)

            class_type_matcher = compile_pattern('"Class": "(.+Part)",?').search(line)
            if class_type_matcher is not None and class_type_matcher.group(1) not in self.types:
                print compile_pattern('"Class": "(.+Part)",?').search(line).group(1) + \
                      ' type on line ' + str(self.line_counter) + ' has not been implemented'

    def convert(self, class_type=''):
        """Converts all the collected questions into QTI XML files and zips them up together.

        :param str class_type: The interaction type conversion is limited to.
        """
        if not self.questions:
            raise ValueError('questions[] cannot be empty')

        if (isinstance(class_type, str) and class_type) and class_type in globals():
            class_type = reduce(getattr, class_type.split("."), modules[__name__])
        elif not isinstance(class_type, str):
            raise TypeError('class_type needs to be a str type')
        else:
            class_type = None

        if class_type:
            for interaction in self.questions:
                if isinstance(interaction, class_type):
                    interaction.to_qti()
        else:
            for interaction in self.questions:
                interaction.to_qti()

        if not self.path:
            zip_file = \
                ZipFile('export-' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.zip', 'w')

            for question in listdir(dirname(__file__)):
                if question.endswith('.zip') and not question.startswith('export-'):
                    zip_file.write(question)
                    remove(question)

        else:
            export_path = compile_pattern('([\\/].*[\\/]).*[\\/]').search(self.path).group(1)
            zip_file = \
                ZipFile(export_path + 'export-' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') +
                        '.zip', 'w')

            for question_name in listdir(dirname(self.path)):
                question = self.path + question_name
                zip_file.write(question, question_name)

            rmtree(self.path)

    class Word(object):
        """Creates a Word with associated content and identifier.

        :param str content: Content of the word.
        :param str wid: Identifier of the word.
        """
        def __init__(self, content, wid):
            if isinstance(content, str):
                self.content = content
            else:
                raise TypeError('content needs to be a str type')

            if isinstance(wid, str):
                self.wid = wid
            else:
                raise TypeError('wid needs to be a str type')


class QTICollector(object):
    """Traverses a given QTI XML file and collects data so that it can be converted.

    :param str file_name: The file's name.
    :param str path: The path of the file to be created.
    """
    def __init__(self, file_name, path=''):
        if isinstance(file_name, str):
            self.file_name = file_name
        else:
            raise TypeError('file_name needs to be a str type')

        if isinstance(path, str):
            self.path = path
        else:
            raise TypeError('path needs to be a str type')

        if not file_name.lower().endswith('.xml'):
            raise TypeError('file_name must be a .xml file')

        tree = parse(file_name)
        self.root = tree.getroot()

        self.name_space = '{http://www.imsglobal.org/xsd/imsqti_v2p2}'

        if not self.root.tag.startswith(self.name_space):
            raise NotImplementedError('must use namespace ' + self.name_space)

        self.identifier = ''
        self.prompt = ''
        self.title = ''
        self.value_single = ''

        self.check_0 = []
        self.check_1 = []
        self.choices = []
        self.labels = []
        self.solutions = []
        self.temp = []
        self.wordbank = []
        self.values = []

        self.collect()

    def collect(self):
        """Collects data from the source QTI XML file and converts it at the end."""
        self.identifier = self.root.attrib['identifier']
        self.title = self.root.attrib['title']

        if self.root.find(self.name_space + 'itemBody').\
                find(self.name_space + 'choiceInteraction') is not None:
            response_declaration = self.root.find(self.name_space + 'responseDeclaration')
            correct_response = response_declaration.find(self.name_space + 'correctResponse')
            for correct_value in correct_response:
                self.temp.append(correct_value.text)

            item_body = self.root.find(self.name_space + 'itemBody')
            choice_interaction = item_body.find(self.name_space + 'choiceInteraction')
            prompt = choice_interaction.find(self.name_space + 'prompt')
            self.prompt = prompt.text

            for index, choice in \
                    enumerate(choice_interaction.findall(self.name_space + 'simpleChoice')):
                self.choices.append(choice.text)
                if choice.attrib['identifier'] in self.temp:
                    self.values.append(str(index))

            choice_output = ChoiceInteraction(self.identifier, self.prompt, self.title, self.values,
                                              self.choices, self.path)
            choice_output.to_nti()

        elif self.root.find(self.name_space + 'itemBody').\
                find(self.name_space + 'extendedTextInteraction') is not None:
            item_body = self.root.find(self.name_space + 'itemBody')
            extended_text_interaction = item_body.find(self.name_space + 'extendedTextInteraction')
            prompt = extended_text_interaction.find(self.name_space + 'prompt')
            self.prompt = prompt.text

            extended_output = ExtendedTextInteraction(self.identifier, self.prompt, self.title,
                                                      self.path)
            extended_output.to_nti()

        elif self.root.find(self.name_space + 'itemBody').\
                find(self.name_space + 'matchInteraction') is not None:
            response_declaration = self.root.find(self.name_space + 'responseDeclaration')
            correct_response = response_declaration.find(self.name_space + 'correctResponse')

            for value in correct_response:
                string = value.text
                modified_0 = sub(r'[^\w]', ' ', string).split()[0]
                modified_1 = sub(r'[^\w]', ' ', string).split()[1]
                self.values.append(modified_0)
                self.labels.append(modified_1)
                self.check_0.append(modified_0)
                self.check_1.append(modified_1)

            num = 0
            temp_0 = list(self.values)
            for index, value in enumerate(self.values):
                if self.values[index] in self.values[:index]:
                    temp_0[index] = self.values.index(value)
                else:
                    temp_0[index] = num
                    num = num + 1
            self.values = list(temp_0)

            num = 0
            temp_1 = list(self.labels)
            for index, label in enumerate(self.labels):
                if self.labels[index] in self.labels[:index]:
                    temp_1[index] = self.labels.index(label)
                else:
                    temp_1[index] = num
                    num = num + 1
            self.labels = list(temp_1)

            for index in range(max(len(self.values), len(self.labels))):
                self.solutions.append(str(self.values.pop(0)) + ' ' + str(self.labels.pop(0)))

            item_body = self.root.find(self.name_space + 'itemBody')
            match_interaction = item_body.find(self.name_space + 'matchInteraction')
            prompt = match_interaction.find(self.name_space + 'prompt')
            self.prompt = prompt.text

            self.labels = []
            self.values = []
            for simple_match_set in match_interaction.findall(self.name_space + 'simpleMatchSet'):
                for index, choice in enumerate(simple_match_set):
                    identifier = choice.attrib['identifier']
                    if identifier in self.check_0:
                        self.labels.insert(self.check_0.index(identifier), choice.text)
                    elif identifier in self.check_1:
                        self.values.insert(self.check_1.index(identifier), choice.text)

            match_output = MatchInteraction(self.identifier, self.prompt, self.title, self.labels,
                                            self.solutions, self.values, self.path)
            match_output.to_nti()

        elif self.root.find(self.name_space + 'itemBody').find(self.name_space + 'p') is not None:
            if self.root.find(self.name_space + 'itemBody').find(self.name_space + 'p').\
               find(self.name_space + 'textEntryInteraction') is not None:

                response_declaration = self.root.find(self.name_space + 'responseDeclaration')
                mapping = response_declaration.find(self.name_space + 'mapping')

                if mapping is not None:
                    for map_entry in mapping:
                        self.values.append(map_entry.attrib['mapKey'])
                else:
                    correct_response = response_declaration.\
                        find(self.name_space + 'correctResponse')
                    correct_value = correct_response.find(self.name_space + 'value')
                    self.value_single = correct_value.text
                    try:
                        float(self.value_single)
                    except ValueError:
                        self.values.append(self.value_single)

                item_body = self.root.find(self.name_space + 'itemBody')
                prompt = item_body.find(self.name_space + 'p')
                text_interaction = prompt.find(self.name_space + 'textEntryInteraction')
                length = int(text_interaction.attrib['expectedLength'])

                if compile_pattern(r'\n\s{6}').match(prompt.text) is not None and self.values:
                    self.prompt = sub(r'\n\s{6}', '', prompt.text) + '_' * length + '.'
                else:
                    self.prompt = sub(r'\n\s{6}', '', prompt.text)

                if self.values:
                    text_output = TextEntryInteraction(self.identifier, self.prompt, self.title,
                                                       self.values, False, self.path)
                    text_output.to_nti()
                else:
                    math_output = TextEntryInteraction(self.identifier, self.prompt, self.title,
                                                       self.value_single, True, self.path)
                    math_output.to_nti()

            elif self.root.find(self.name_space + 'itemBody').find(self.name_space + 'p').\
                    find(self.name_space + 'inlineChoiceInteraction') is not None:
                self.prompt = []

                for response_declaration in self.root:
                    try:
                        if response_declaration.attrib['baseType'] == 'identifier':
                            correct_response = response_declaration. \
                                find(self.name_space + 'correctResponse')
                            correct_value = correct_response.find(self.name_space + 'value')
                            self.solutions.append(str(correct_value.text))
                    except KeyError:
                        pass

                item_body = self.root.find(self.name_space + 'itemBody')
                prompt = item_body.find(self.name_space + 'p')
                inline_choice_interaction = prompt.find(self.name_space + 'inlineChoiceInteraction')

                index = 0
                for inline_choice in inline_choice_interaction:
                    if inline_choice.attrib['identifier'] in self.solutions:
                        self.solutions[self.solutions.index(inline_choice.attrib['identifier'])]\
                            = str(index)
                        self.wordbank.append(self.Word(inline_choice.text, str(index)))
                    else:
                        self.wordbank.append(self.Word(inline_choice.text, str(index)))
                    index = index + 1

                for integer in self.solutions:
                    self.labels.append(str('%03d' % (int(integer) + 1,)))

                self.prompt.append(sub(r'\n\s{4,6}', '', prompt.text))

                for tail in prompt:
                    self.prompt.append(sub(r'\n\s{4,6}', '', tail.tail))

                temp = self.prompt.pop(0)
                for label in self.labels:
                    temp = temp + '<input type=\\"blankfield\\" name=\\"' + label + '\\" />'
                    temp = temp + self.prompt.pop(0)
                self.prompt = temp

                inline_output = InlineChoiceInteraction(self.identifier, self.prompt, self.title,
                                                        self.labels, self.solutions, self.wordbank,
                                                        self.path)
                inline_output.to_nti()

        elif self.root.find(self.name_space + 'itemBody').\
                find(self.name_space + 'uploadInteraction') is not None:
            item_body = self.root.find(self.name_space + 'itemBody')
            upload_interaction = item_body.find(self.name_space + 'uploadInteraction')
            prompt = upload_interaction.find(self.name_space + 'prompt')
            self.prompt = prompt.text

            upload_output = UploadInteraction(self.identifier, self.prompt, self.title, self.path)
            upload_output.to_nti()

        else:
            raise NotImplementedError('there is no valid question type to convert')

    class Word(object):
        """Creates a Word with associated content and identifier.

        :param str content: Content of the word.
        :param str wid: Identifier of the word.
        """
        def __init__(self, content, wid):
            if isinstance(content, str):
                self.content = content
            else:
                raise TypeError('content needs to be a str type')

            if isinstance(wid, str):
                self.wid = wid
            else:
                raise TypeError('wid needs to be a str type')


class Extractor(object):
    """Extracts a given zip containing QTI XML zip files into a zip containing NTI JSON files.

    :param str path: The path of the file to be extracted.
    """
    def __init__(self, path):
        if isinstance(path, str):
            self.path = path
        else:
            raise TypeError('path needs to be a str type')

        self.extract()

    def extract(self):
        """Extracts the given zip and converts all its containing questions into NTI JSON files."""
        zip_file = ZipFile(self.path, 'r')
        path = self.path[:-4]
        zip_file.extractall(path)
        for zip_ref in zip_file.namelist():
            extracted = ZipFile(path + '/' + zip_ref, 'r')
            extracted.extractall(path + '/' + zip_ref[:-4] + '/')
            remove(path + '/' + zip_ref[:-4] + '/' + 'imsmanifest.xml')
            qti_file = listdir(path + '/' + zip_ref[:-4] + '/')[0]
            QTICollector(path + '/' + zip_ref[:-4] + '/' + qti_file, path + '/')
            rmtree(path + '/' + zip_ref[:-4] + '/')
            remove(path + '/' + zip_ref)
        zip_file.close()

        zip_json = ZipFile(dirname(zip_file.filename) + '/nti-' +
                           datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.zip', 'w')
        for json_file in listdir(path + '/'):
            if json_file.endswith('.json'):
                zip_json.write(path + '/' + json_file, 'nti-' +
                               datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '/' + json_file)
                remove(path + '/' + json_file)
        rmtree(path + '/')


PARSER = ArgumentParser(description='Export/Import NTI/QTI packages.')
PARSER.add_argument('file', type=file, help='This is the file to be parsed.')
ARGS = None
try:
    ARGS = PARSER.parse_args()
except IOError:
    print 'file not found'
    sys_exit(1)

if ARGS.file.name.endswith('.json'):
    NTICollector(basename(ARGS.file.name),
                 realpath(ARGS.file.name)[:-5] + b2a_hex(urandom(16)) + '/')
elif ARGS.file.name.endswith('.zip'):
    Extractor(realpath(ARGS.file.name))
elif ARGS.file.name.endswith('.xml'):
    QTICollector(realpath(ARGS.file.name), dirname(realpath(ARGS.file.name)) + '/')
else:
    print 'file cannot end in ' + splitext(realpath(ARGS.file.name))[1]
    print 'file must end in either .json, .zip, or .xml'
