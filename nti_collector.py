from choice_interaction__parser import ChoiceInteraction
from extended_text_interaction__parser import ExtendedTextInteraction
from text_entry_interaction__parser import TextEntryInteraction
from upload_interaction__parser import UploadInteraction

from re import compile


class NTICollector(object):

    def __init__(self, file_name):
        if type(file_name) is str:
            self.file_name = file_name
        else:
            raise TypeError('File name needs to be a str type.')

        class_re = '"Class": "(.+Part)",?'
        identifier_re = '"(NTIID|ntiid)": "(tag:.+_(.+)\.naq\.qid(\..+))",?'
        prompt_re = '"content": "(.*)",?'
        choice_re = '"<a name=.+>.*</a>.*<p class=.+id=.+>(.+)</p>"'
        value_mc__re = '"value": (\\d),?'
        value_mc_ma__re = '(\\d),?'
        value_fr__re = '"value": "(.+)",?'

        self.class_pattern = compile(class_re)
        self.identifier_pattern = compile(identifier_re)
        self.prompt_pattern = compile(prompt_re)
        self.choice_pattern = compile(choice_re)
        self.value_mc__pattern = compile(value_mc__re)
        self.value_mc_ma__pattern = compile(value_mc_ma__re)
        self.value_fr__pattern = compile(value_fr__re)

        self.line_counter = 0
        self.total_lines = self.lines()
        self.identifier = ''
        self.prompt = ''
        self.title = ''
        self.value_single = ''
        self.choices = []
        self.values = []
        self.questions = []


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
        lines = 0
        for line in open(self.file_name):
            lines += 1
        return lines
