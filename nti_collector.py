from re import compile as compile_pattern

from parsers import ChoiceInteraction
from parsers import ExtendedTextInteraction
from parsers import InlineChoiceInteraction
from parsers import MatchInteraction
from parsers import TextEntryInteraction
from parsers import UploadInteraction


class NTICollector(object):

    def __init__(self, file_name):
        if isinstance(file_name, str):
            self.file_name = file_name
        else:
            raise TypeError('file_name needs to be a str type')

        if not file_name.lower().endswith('.json'):
            raise TypeError('file_name must be a .json file')

        self.line_counter = 0
        self.total_lines = sum(1 for line in open(file_name) if line.rstrip())

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
                self.questions.append(UploadInteraction(self.identifier, self.prompt, self.title))

            if '"Class": "FillInTheBlankWithWordBankPart",' in line:
                while '"Class": "Question"' not in line and self.line_counter is not \
                        self.total_lines:
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

                            matcher = compile_pattern('"(\\d)"(?!:)').search(line)
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
                                                              self.solutions, self.words, True))

                self.labels = []
                self.solutions = []
                self.words = []

            if '"Class": "FreeResponsePart",' in line:
                while '"Class": "Question"' not in line and self.line_counter is not \
                        self.total_lines:
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
                    TextEntryInteraction(self.identifier, self.prompt, self.title, self.values))

                self.choices = []
                self.values = []

            if '"Class": "MatchingPart"' in line or '"Class": "OrderingPart"' in line:
                matcher = compile_pattern('"Class": "(.+Part)",?').search(line)
                if matcher is not None:
                    self.class_type = matcher.group(1)
                while '"Class": "Question"' not in line and self.line_counter is not \
                        self.total_lines:
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
                                         self.solutions, self.values))

                elif self.class_type == 'OrderingPart':
                    self.questions.append(
                        MatchInteraction(self.identifier, self.prompt, self.title, self.labels,
                                         self.solutions, self.values))

                self.labels = []
                self.values = []
                self.solutions = []

            if '"Class": "ModeledContentPart"' in line:
                self.questions.append(ExtendedTextInteraction(self.identifier, self.prompt,
                                                              self.title))

            if '"Class": "MultipleChoicePart",' in line:
                while '"Class": "Question"' not in line and self.line_counter is not \
                        self.total_lines:
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
                                                        self.values, self.choices))

                self.choices = []
                self.values = []

            if '"Class": "MultipleChoiceMultipleAnswerPart",' in line:
                while '"Class": "Question"' not in line and self.line_counter is not \
                        self.total_lines:
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
                                                        self.values, self.choices))

                self.choices = []
                self.values = []

            if '"Class": "SymbolicMathPart",' in line:
                while '"Class": "Question"' not in line and self.line_counter is not \
                        self.total_lines:
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
                                         self.value_single, True))

                self.choices = []
                self.values = []

            class_type_matcher = compile_pattern('"Class": "(.+Part)",?').search(line)
            if class_type_matcher is not None and class_type_matcher.group(1) not in self.types:
                print compile_pattern('"Class": "(.+Part)",?').search(line).group(1) + \
                      ' type on line ' + str(self.line_counter) + ' has not been implemented'

    def convert(self, qti=True, nti=True):
        if not self.questions:
            raise ValueError('questions[] cannot be empty')

        if qti:
            for interaction in self.questions:
                interaction.to_qti()

        if nti:
            for interaction in self.questions:
                interaction.to_nti()

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
