from parsers import ChoiceInteraction
from parsers import ExtendedTextInteraction
from match_interaction__parser import MatchInteraction
from parsers import TextEntryInteraction
from parsers import UploadInteraction

from re import compile as compile_pattern


class NTICollector(object):

    def __init__(self, file_name):
        if type(file_name) is str:
            self.file_name = file_name
        else:
            raise TypeError('File name needs to be a str type.')

        class_re = '"Class": "(.+Part)",?'
        self.class_pattern = compile_pattern(class_re)

        identifier_re = '"(NTIID|ntiid)": "(tag:.+_(.+)\.naq\.qid(\..+))",?'
        self.identifier_pattern = compile_pattern(identifier_re)

        prompt_re = '"content": "(.*)",?'
        self.prompt_pattern = compile_pattern(prompt_re)

        choice_re = '"<a name=.+>.*</a>.*<p class=.+id=.+>(.+)</p>"'
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

        self.choices = []
        self.labels = []
        self.questions = []
        self.solutions = []
        self.values = []

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
                    self.title = str(matcher.group(3)) + str(matcher.group(4))

            if '"content":' in line:
                matcher = self.prompt_pattern.search(line)
                if matcher is not None:
                    self.prompt = matcher.group(1)

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
                                self.choices.append(matcher.group(0))

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

                self.questions.append(
                    ChoiceInteraction(self.identifier, self.prompt, self.title, self.values, self.choices))

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
                                self.choices.append(matcher.group(0))

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

                self.questions.append(
                    ChoiceInteraction(self.identifier, self.prompt, self.title, self.values, self.choices))

                self.choices = []
                self.values = []

            if '"Class": "MatchingPart"' in line:
                while '"Class": "Question"' not in line:
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

                self.questions.append(
                    MatchInteraction(self.identifier, self.prompt, self.title, self.labels, self.solutions,
                                     self.values))

                self.labels = []
                self.values = []
                self.solutions = []

            if '"Class": "ModeledContentPart"' in line:
                self.questions.append(ExtendedTextInteraction(self.identifier, self.prompt, self.title))

            if '"Class": "FreeResponsePart",' in line:
                while '"Class": "Question"' not in line and self.line_counter is not self.total_lines:
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

            if '"Class": "SymbolicMathPart",' in line:
                while '"Class": "Question"' not in line and self.line_counter is not self.total_lines:
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
                    TextEntryInteraction(self.identifier, self.prompt, self.title, self.value_single, True))

                self.choices = []
                self.values = []

            if '"Class": "FilePart"' in line:
                self.questions.append(UploadInteraction(self.identifier, self.prompt, self.title))

    def convert(self, qti, nti):
        if not self.questions:
            raise ValueError('Questions[] cannot be empty')

        if qti:
            for interaction in self.questions:
                interaction.to_qti()

        if nti:
            for interaction in self.questions:
                interaction.to_qti()

    def lines(self):
        i = 0
        for i, l in enumerate(open(self.file_name)):
            pass
        return i + 1
