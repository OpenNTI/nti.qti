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

data = ['text', 'foo2', 'foo1', 'sample', 'foo']
indexes = [i for i, val in enumerate(data) if 'foo' in val]

print indexes

def recursive_iter(obj):
    if isinstance(obj, dict):
        for item in obj.values():
            for item in recursive_iter(item):
                yield item
    elif any(isinstance(obj, t) for t in (list, tuple)):
        for item in obj:
            for item in recursive_iter(item):
                yield item
    else:
        yield obj

data = load(open('assessment_index.json'))
for item in recursive_iter(data):
    print(item)

listing = ['a', 'b', 'c', 'b']
print listing.index('b')