from datetime import datetime

from os import listdir
from os import remove

from os.path import dirname

from shutil import rmtree

from zipfile import ZipFile

from qti_collector import QTICollector


class Extractor(object):
    def __init__(self, path):
        if isinstance(path, str):
            self.path = path
        else:
            raise TypeError('path needs to be a str type')

        self.extract()

    def extract(self):
        zip_file = ZipFile(self.path, 'r')
        zip_file.extractall(self.path[:-4])
        for zip_ref in zip_file.namelist():
            extracted = ZipFile(self.path[:-4] + '/' + zip_ref, 'r')
            extracted.extractall(self.path[:-4] + '/' + zip_ref[:-4] + '/')
            remove(self.path[:-4] + '/' + zip_ref[:-4] + '/' + 'imsmanifest.xml')
            qti_file = listdir(self.path[:-4] + '/' + zip_ref[:-4] + '/')[0]
            QTICollector(self.path[:-4] + '/' + zip_ref[:-4] + '/' + qti_file,
                         dirname(zip_file.filename) + '/')
            rmtree(self.path[:-4] + '/' + zip_ref[:-4] + '/')
            remove(self.path[:-4] + '/' + zip_ref)
        rmtree(self.path[:-4] + '/')
        zip_file.close()

        zip_json = ZipFile(dirname(zip_file.filename) + '/nti-' +
                           datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.zip', 'w')
        for json_file in listdir(dirname(zip_file.filename) + '/'):
            if json_file.endswith('.json'):
                zip_json.write(dirname(zip_file.filename) + '/' + json_file, 'nti-' +
                               datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '/' + json_file)
                remove(dirname(zip_file.filename) + '/' + json_file)


Extractor('/Users/noah.monaghan/Documents/test/export-2018-03-05_13-33-20.zip')
