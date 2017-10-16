from choice_interaction_parser import ChoiceInteraction

from re import compile


class NTICollector:

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

        self.class_pattern = compile(class_re)
        self.identifier_pattern = compile(identifier_re)
        self.prompt_pattern = compile(prompt_re)
        self.choice_pattern = compile(choice_re)
        self.value_mc__pattern = compile(value_mc__re)

        self.line_counter = 0
        self.identifier = ''
        self.prompt = ''
        self.title = ''
        self.choices = []
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
                            self.prompt = matcher.group(1)

                    if '"value":' in line:
                        matcher = self.value_mc__pattern.search(line)
                        if matcher is not None:
                            self.values.append(matcher.group(1))

                ChoiceInteraction(self.identifier, self.prompt, self.values, self.choices, self.title).to_qti()
                ChoiceInteraction(self.identifier, self.prompt, self.values, self.choices, self.title).to_nti()

                self.choices = []
                self.values = []
