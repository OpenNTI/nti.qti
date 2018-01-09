from parsers import ChoiceInteraction
from parsers import ExtendedTextInteraction
from parsers import MatchInteraction
from parsers import TextEntryInteraction
from parsers import UploadInteraction

from re import sub

from xml.etree import ElementTree


class QTICollector(object):

    def __init__(self, file_name):
        if type(file_name) is str:
            self.file_name = file_name
        else:
            raise TypeError('file_name needs to be a str type')

        if not file_name.lower().endswith('.xml'):
            raise TypeError('file_name must be a .xml file')

        tree = ElementTree.parse(file_name)
        self.root = tree.getroot()

        self.ns = '{http://www.imsglobal.org/xsd/imsqti_v2p2}'

        self.identifier = ''
        self.title = ''
        self.prompt = ''

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

        if self.root.find(self.ns + 'itemBody').find(self.ns + 'choiceInteraction') is not None:
            response_declaration = self.root.find(self.ns + 'responseDeclaration')
            correct_response = response_declaration.find(self.ns + 'correctResponse')
            for correct_value in correct_response:
                self.temp.append(correct_value.text)

            item_body = self.root.find(self.ns + 'itemBody')
            choice_interaction = item_body.find(self.ns + 'choiceInteraction')
            prompt = choice_interaction.find(self.ns + 'prompt')
            self.prompt = prompt.text

            index = 0
            for choice in choice_interaction.findall(self.ns + 'singleChoice'):
                self.choices.append(choice.text)
                if choice.attrib['identifier'] in self.temp:
                    self.values.append(str(index))
                index = index + 1

            choice_output = ChoiceInteraction(self.identifier, self.prompt, self.title, self.values, self.choices)
            choice_output.to_nti()

        if self.root.find(self.ns + 'itemBody').find(self.ns + 'extendedTextInteraction') is not None:
            item_body = self.root.find(self.ns + 'itemBody')
            choice_interaction = item_body.find(self.ns + 'choiceInteraction')
            prompt = choice_interaction.find(self.ns + 'prompt')
            self.prompt = prompt.text

            extended_output = ExtendedTextInteraction(self.identifier, self.prompt, self.title)
            extended_output.to_nti()

        if self.root.find(self.ns + 'itemBody').find(self.ns + 'matchInteraction') is not None:
            response_declaration = self.root.find(self.ns + 'responseDeclaration')
            correct_response = response_declaration.find(self.ns + 'correctResponse')

            for value in correct_response:
                string = value.text
                modified_0 = sub('[^\w]', ' ', string).split()[0]
                modified_1 = sub('[^\w]', ' ', string).split()[1]
                self.values.append(modified_0)
                self.labels.append(modified_1)
                self.check_0.append(modified_0)
                self.check_1.append(modified_1)

            index = 0
            num = 0
            temp_0 = list(self.values)
            for value in self.values:
                if self.values[index] in self.values[:index]:
                    temp_0[index] = self.values.index(value)
                else:
                    temp_0[index] = num
                    num = num + 1
                index = index + 1
            self.values = list(temp_0)

            index = 0
            num = 0
            temp_1 = list(self.labels)
            for label in self.labels:
                if self.labels[index] in self.labels[:index]:
                    temp_1[index] = self.labels.index(label)
                else:
                    temp_1[index] = num
                    num = num + 1
                index = index + 1
            self.labels = list(temp_1)

            for index in range(max(len(self.values), len(self.labels))):
                self.solutions.append(str(self.values.pop(0)) + ' ' + str(self.labels.pop(0)))

            item_body = self.root.find(self.ns + 'itemBody')
            match_interaction = item_body.find(self.ns + 'matchInteraction')
            prompt = match_interaction.find(self.ns + 'prompt')
            self.prompt = prompt.text

            self.labels = []
            self.values = []
            for simple_match_set in match_interaction.findall(self.ns + 'simpleMatchSet'):
                index = 0
                for choice in simple_match_set:
                    cai = choice.attrib['identifier']
                    if cai in self.check_0:
                        self.labels.insert(self.check_0.index(cai), choice.text)
                    elif cai in self.check_1:
                        self.values.insert(self.check_1.index(cai), choice.text)
                    index = index + 1

            match_output = \
                MatchInteraction(self.identifier, self.prompt, self.title, self.labels, self.solutions, self.values)
            match_output.to_nti()

        if self.root.find(self.ns + 'itemBody').find(self.ns + 'uploadInteraction') is not None:
            item_body = self.root.find(self.ns + 'itemBody')
            upload_interaction = item_body.find(self.ns + 'uploadInteraction')
            prompt = upload_interaction.find(self.ns + 'prompt')
            self.prompt = prompt.text

            upload_output = UploadInteraction(self.identifier, self.prompt, self.title)
            upload_output.to_nti()

        else:
            raise NotImplementedError('there is no valid question type to convert')
