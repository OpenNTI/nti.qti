from json import dumps
from json import load

from io import open

from re import match

from pprint import pprint


class NTICollector(object):

    def __init__(self, file_name):
        if type(file_name) is str:
            self.file_name = file_name
        else:
            raise TypeError('File name needs to be a str type.')

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
        data = load(open(self.file_name))
        nti_file = open(self.file_name.replace('.json', '') + '_parsed.txt', 'w+', encoding='utf-8')
        nti_file.write(unicode(data))
        print data \
        ['Items'] \
        ['tag:nextthought.com,2011-10:NTIAlpha-HTML-NTI1000_TestCourse.test_course'] \
        ['Items'] \
        ['tag:nextthought.com,2011-10:NTIAlpha-HTML-NTI1000_TestCourse.lesson:LSTD1153_unit1'] \
        ['Items']
        for item in data['Items']:
            print item



idiot = NTICollector('assessment_index.json')
idiot.collect()

data = ['text', 'foo2', 'foo1', 'sample']
indeces = (i for i,val in enumerate(data) if match('foo', val))

print indeces('foo')