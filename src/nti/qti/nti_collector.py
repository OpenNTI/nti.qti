from re import compile as compile_pattern

from src.nti.qti.parsers import ChoiceInteraction
from src.nti.qti.parsers import ExtendedTextInteraction
from src.nti.qti.parsers import MatchInteraction
from src.nti.qti.parsers import TextEntryInteraction
from src.nti.qti.parsers import UploadInteraction


class NTICollector(object):

    def __init__(self, file_name):
        if isinstance(file_name, str):
            self.file_name = file_name
        else:
            raise TypeError('file_name needs to be a str type')

        if not file_name.lower().endswith('.json'):
            raise TypeError('file_name must be a .json file')

        class_re = '"Class": "(.+Part)",?'
        self.class_pattern = compile_pattern(class_re)

        identifier_re = r'"(NTIID|ntiid)": "(tag:.+_(.+)\.naq\.qid(\.content)?(\..+))",?'
        self.identifier_pattern = compile_pattern(identifier_re)

        prompt_re = '"content": "(.*)",?'
        self.prompt_pattern = compile_pattern(prompt_re)

        choice_re = '"(<a name=.+>.*</a>.*<p class=.+id=.+>(.+)</p>)"'
        self.choice_pattern = compile_pattern(choice_re)

        pair_re = '"(\\d+)":( \\d+),?'
        self.pair_pattern = compile_pattern(pair_re)

        value_mc__re = '"value": (\\d),?'
        self.value_mc__pattern = compile_pattern(value_mc__re)

        value_mc_ma__re = '(\\d),?'
        self.value_mc_ma__pattern = compile_pattern(value_mc_ma__re)

        value_fr__re = '"value": "(.+)",?'
        self.value_fr__pattern = compile_pattern(value_fr__re)

        value_ma__re = '"(.+)",?'
        self.value_ma__pattern = compile_pattern(value_ma__re)

        self.line_counter = 0

        self.total_lines = self.lines()

        self.identifier = ''
        self.prompt = ''
        self.title = ''
        self.value_single = ''
        self.class_type = ''

        self.choices = []
        self.labels = []
        self.questions = []
        self.solutions = []
        self.values = []

        self.types = ('MultipleChoicePart', 'MultipleChoiceMultipleAnswerPart', 'OrderingPart',
                      'MatchingPart', 'FreeResponsePart', 'ModeledContentPart', 'FilePart',
                      'SymbolicMathPart', 'AssignmentPart')

    def collect(self):
        infile = open(self.file_name, 'r')
        for line in infile:
            self.line_counter += 1

            if '"Class": "Poll",' in line:
                while '"Class": "Question"' not in line:
                    self.line_counter += 1
                    line = next(infile)

            if ('"NTIID":' or '"ntiid":') in line:
                matcher = self.identifier_pattern.search(line)
                if matcher is not None:
                    self.identifier = str(matcher.group(2))
                    self.title = str(matcher.group(3)) + str(matcher.group(5))

            if '"content":' in line:
                matcher = self.prompt_pattern.search(line)
                if matcher is not None:
                    self.prompt = matcher.group(1)

            if '"Class": "FilePart"' in line:
                self.questions.append(UploadInteraction(self.identifier, self.prompt, self.title))

            if '"Class": "FreeResponsePart",' in line:
                while '"Class": "Question"' not in line and self.line_counter is not \
                        self.total_lines:
                    self.line_counter += 1
                    line = next(infile)

                    if '"value": ' in line:
                        matcher = self.value_fr__pattern.search(line)
                        if matcher is not None:
                            self.values.append(str(matcher.group(1)))

                    if '"content": "",' in line:
                        self.line_counter += 1
                        line = next(infile)
                    elif '"content":' in line:
                        matcher = self.prompt_pattern.search(line)
                        if matcher is not None:
                            self.prompt += ' ' + matcher.group(1)

                self.questions.append(
                    TextEntryInteraction(self.identifier, self.prompt, self.title, self.values))

                self.choices = []
                self.values = []

            if '"Class": "MatchingPart"' in line or '"Class": "OrderingPart"' in line:
                matcher = self.class_pattern.search(line)
                if matcher is not None:
                    self.class_type = matcher.group(1)
                while '"Class": "Question"' not in line and self.line_counter is not \
                        self.total_lines:
                    self.line_counter += 1
                    line = next(infile)

                    if '"labels": [' in line:
                        while ']' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = self.value_ma__pattern.search(line)
                            if matcher is not None:
                                self.labels.append(str(matcher.group(1)))

                    if '"value": {' in line:
                        while '}' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = self.pair_pattern.search(line)
                            if matcher is not None:
                                self.solutions.append(str(matcher.group(1) + matcher.group(2)))

                    if '"values": [' in line:
                        while ']' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = self.value_ma__pattern.search(line)
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
                while '"weight":' not in line:
                    self.line_counter += 1
                    line = next(infile)

                    if '"choices": [' in line:
                        while '],' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = self.choice_pattern.search(line)
                            if matcher is not None:
                                self.choices.append(matcher.group(1))

                    if '"content": "",' in line:
                        self.line_counter += 1
                        line = next(infile)
                    elif '"content":' in line:
                        matcher = self.prompt_pattern.search(line)
                        if matcher is not None:
                            self.prompt += ' ' + matcher.group(1)

                    if '"value":' in line:
                        matcher = self.value_mc__pattern.search(line)
                        if matcher is not None:
                            self.values.append(matcher.group(1))

                self.questions.append(ChoiceInteraction(self.identifier, self.prompt, self.title,
                                                        self.values, self.choices))

                self.choices = []
                self.values = []

            if '"Class": "MultipleChoiceMultipleAnswerPart",' in line:
                while '"weight":' not in line:
                    self.line_counter += 1
                    line = next(infile)

                    if '"choices": [' in line:
                        while '],' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = self.choice_pattern.search(line)
                            if matcher is not None:
                                self.choices.append(matcher.group(1))

                    if '"content": "",' in line:
                        self.line_counter += 1
                        line = next(infile)
                    elif '"content":' in line:
                        matcher = self.prompt_pattern.search(line)
                        if matcher is not None:
                            self.prompt += ' ' + matcher.group(1)

                    if '"value": [' in line:
                        while '],' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = self.value_mc_ma__pattern.search(line)
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
                        matcher = self.prompt_pattern.search(line)
                        if matcher is not None:
                            self.prompt += ' ' + matcher.group(1)

                    if '"value": ' in line:
                        matcher = self.value_fr__pattern.search(line)
                        if matcher is not None:
                            self.value_single = str(matcher.group(1))

                self.questions.append(
                    TextEntryInteraction(self.identifier, self.prompt, self.title,
                                         self.value_single, True))

                self.choices = []
                self.values = []

            class_type_matcher = self.class_pattern.search(line)
            if class_type_matcher is not None and class_type_matcher.group(1) not in self.types:
                print self.class_pattern.search(line).group(1) + ' type on line ' + \
                      str(self.line_counter) + ' has not been implemented'

    def convert(self, qti=True, nti=True):
        if not self.questions:
            raise ValueError('questions[] cannot be empty')

        if qti:
            for interaction in self.questions:
                interaction.to_qti()

        if nti:
            for interaction in self.questions:
                interaction.to_nti()

    def lines(self):
        i = 0
        for i, l in enumerate(open(self.file_name)):
            pass
        return i + 1
