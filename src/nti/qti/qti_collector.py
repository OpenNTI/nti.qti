from re import compile as compile_pattern
from re import sub

from xml.etree import ElementTree

from src.nti.qti.parsers import ChoiceInteraction
from src.nti.qti.parsers import ExtendedTextInteraction
from src.nti.qti.parsers import MatchInteraction
from src.nti.qti.parsers import TextEntryInteraction
from src.nti.qti.parsers import UploadInteraction


class QTICollector(object):

    def __init__(self, file_name):
        if isinstance(file_name, str):
            self.file_name = file_name
        else:
            raise TypeError('file_name needs to be a str type')

        if not file_name.lower().endswith('.xml'):
            raise TypeError('file_name must be a .xml file')

        tree = ElementTree.parse(file_name)
        self.root = tree.getroot()

        self.name_space = '{http://www.imsglobal.org/xsd/imsqti_v2p2}'

        if not self.root.tag.startswith(self.name_space):
            raise NotImplementedError('must use namespace ' + self.name_space)

        self.identifier = ''
        self.title = ''
        self.prompt = ''
        self.value_single = ''

        self.values = []
        self.labels = []
        self.check_0 = []
        self.check_1 = []
        self.solutions = []
        self.temp = []
        self.choices = []

    def collect(self):
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
                    enumerate(choice_interaction.findall(self.name_space + 'singleChoice')):
                self.choices.append(choice.text)
                if choice.attrib['identifier'] in self.temp:
                    self.values.append(str(index))

            choice_output = ChoiceInteraction(self.identifier, self.prompt, self.title, self.values,
                                              self.choices)
            choice_output.to_nti()

        elif self.root.find(self.name_space + 'itemBody').\
                find(self.name_space + 'extendedTextInteraction') is not None:
            item_body = self.root.find(self.name_space + 'itemBody')
            choice_interaction = item_body.find(self.name_space + 'choiceInteraction')
            prompt = choice_interaction.find(self.name_space + 'prompt')
            self.prompt = prompt.text

            extended_output = ExtendedTextInteraction(self.identifier, self.prompt, self.title)
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
                                            self.solutions, self.values)
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
                elif compile_pattern(r'\n\s{6}').match(prompt.text) is not None and not self.values:
                    self.prompt = sub(r'\n\s{6}', '', prompt.text)
                else:
                    raise NotImplementedError('sorry')

                if self.values:
                    text_output = TextEntryInteraction(self.identifier, self.prompt, self.title,
                                                       self.values)
                    text_output.to_nti()
                elif not self.values:
                    math_output = TextEntryInteraction(self.identifier, self.prompt, self.title,
                                                       self.value_single, True)
                    math_output.to_nti()
                else:
                    raise ZeroDivisionError('something is not right')

        elif self.root.find(self.name_space + 'itemBody').\
                find(self.name_space + 'uploadInteraction') is not None:
            item_body = self.root.find(self.name_space + 'itemBody')
            upload_interaction = item_body.find(self.name_space + 'uploadInteraction')
            prompt = upload_interaction.find(self.name_space + 'prompt')
            self.prompt = prompt.text

            upload_output = UploadInteraction(self.identifier, self.prompt, self.title)
            upload_output.to_nti()

        else:
            raise NotImplementedError('there is no valid question type to convert')
