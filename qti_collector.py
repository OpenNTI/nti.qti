from choice_interaction__parser import ChoiceInteraction
from extended_text_interaction__parser import ExtendedTextInteraction
from text_entry_interaction__parser import TextEntryInteraction
from upload_interaction__parser import UploadInteraction

from re import compile


class QTICollector(object):

    def __init__(self, file_name):
        if type(file_name) is str:
            self.file_name = file_name
        else:
            raise TypeError('File name needs to be a str type.')

        all_re = '.+'
        self.all_pattern = compile(all_re)

        base_type__re = 'baseType="(.+)"'
        self.base_type__pattern = compile(base_type__re)

        choice_re = '<simpleAssociableChoice.+identifier=(".+").*>(.+)</simpleAssociableChoice>'
        self.choice_pattern = compile(choice_re)

        pair_re = '<value>(.+) (.+)</value>'
        self.pair_pattern = compile(pair_re)

        prompt_re = '<prompt>(.+)</prompt>'
        self.prompt_pattern = compile(prompt_re)

        value_re = '<value>(.+)</value>'
        self.value_pattern = compile(value_re)

        self.is__directed_pair = False
        self.is_values = False

        self.line_counter = 0
        self.total_lines = self.lines()

        self.base_type = ''
        self.identifier = ''
        self.prompt = ''
        self.title = ''
        self.value_single = ''

        self.choices = []
        self.labels = []
        self.label_identifiers = []
        self.label_solutions = []
        self.questions = []
        self.solutions = []
        self.values = []
        self.value_identifiers = []
        self.value_solutions = []

    def collect(self):
        infile = open(self.file_name, 'r')
        for line in infile:
            self.line_counter += 1

            if '<responseDeclaration' in line:
                while '</responseDeclaration>' not in line:
                    self.line_counter += 1
                    line = next(infile)

                    matcher = self.base_type__pattern.search(line)
                    if matcher is not None:
                        self.base_type = matcher.group(1)

                    if '<correctResponse>' in line:
                        while '</correctResponse>' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            matcher = self.value_pattern.search(line)
                            if matcher is not None:
                                if self.base_type is 'directedPair':
                                    self.is__directed_pair = True
                                    self.label_solutions.append(matcher.group(1))
                                    self.value_solutions.append(matcher.group(2))
                                else:
                                    self.solutions.append(matcher.group(1))

            if '<itemBody>' in line:
                while '</itemBody>' not in line:
                    self.line_counter += 1
                    line = next(infile)

                    if '<matchInteraction' in line:
                        while '</matchInteraction>' not in line:
                            self.line_counter += 1
                            line = next(infile)

                            if '<prompt>' in line:
                                while '</prompt>' not in line:
                                    self.line_counter += 1
                                    line = next(infile)

                                    matcher = self.prompt_pattern.search(line)
                                    if matcher is not None:
                                        self.prompt = str(matcher.group(1))
                                    elif matcher is None:
                                        matcher = self.all_pattern.search(line)
                                        if matcher is not None:
                                            self.prompt = str(matcher.group(0))

                            if '<simpleMatchSet>' in line:
                                if not self.is_values:
                                    while '</simpleMatchSet>' not in line:
                                        self.line_counter += 1
                                        line = next(infile)

                                        matcher = self.choice_pattern.search(line)
                                        if matcher is not None:
                                            self.labels.append(str(matcher.group(2)))
                                            self.label_identifiers.append(str(matcher.group(1)))
                                    self.is_values = True
                                elif self.is_values:
                                    while '</simpleMatchSet>' not in line:
                                        self.line_counter += 1
                                        line = next(infile)

                                        matcher = self.choice_pattern.search(line)
                                        if matcher is not None:
                                            self.values.append(str(matcher.group(2)))
                                            self.value_identifiers.append(str(matcher.group(1)))
                                    self.is_values = False

                        if self.is__directed_pair:
                            temp_list_1 = []
                            temp_list_2 = []

                            for index_i in range(len(self.label_solutions)):
                                for index_j in range(len(self.label_identifiers)):
                                    if self.label_solutions[index_i] is self.label_identifiers[index_j]:
                                        temp_list_1.append(str(index_j))

                            for index_k in range(len(self.value_solutions)):
                                for index_l in range(len(self.value_identifiers)):
                                    if self.value_solutions[index_k] is self.value_identifiers[index_l]:
                                        temp_list_2.append(str(index_l))

                            for index in range(len(temp_list_1)):
                                self.solutions.append(str(temp_list_1[index] + ' ' + temp_list_2[index]))

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
