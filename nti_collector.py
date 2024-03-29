from datetime import datetime

from os import listdir
from os import makedirs
from os import remove

from os.path import dirname
from os.path import isdir

from re import compile as compile_pattern

from shutil import rmtree

from sys import modules

from zipfile import ZipFile

from parsers import ChoiceInteraction
from parsers import ExtendedTextInteraction
from parsers import InlineChoiceInteraction
from parsers import MatchInteraction
from parsers import TextEntryInteraction
from parsers import UploadInteraction


class NTICollector(object):

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

        if not isinstance(class_type, str):
            raise TypeError('class_type needs to be a str type')

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
                                                              self.solutions, self.words, True,
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
        if not self.questions:
            raise ValueError('questions[] cannot be empty')

        if (isinstance(class_type, str) and class_type) and class_type in globals():
            self.class_type = reduce(getattr, class_type.split("."), modules[__name__])
        elif not isinstance(class_type, str):
            raise TypeError('class_type needs to be a str type')
        else:
            self.class_type = None

        if self.class_type:
            for interaction in self.questions:
                if isinstance(interaction, self.class_type):
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

        def __init__(self, content, wid):
            if isinstance(content, str):
                self.content = content
            else:
                raise TypeError('content needs to be a str type')

            if isinstance(wid, str):
                self.wid = wid
            else:
                raise TypeError('wid needs to be a str type')
