from binascii import b2a_hex

from datetime import datetime

from io import open as open_file

from os import remove
from os import urandom

from os.path import basename

from xml.dom.minidom import parseString

from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
from xml.etree.ElementTree import tostring

from zipfile import ZipFile


class Manifest(object):
    def __init__(self, identifier, interaction_type, path='', author='author'):
        if isinstance(identifier, str):
            self.identifier = identifier
        else:
            raise TypeError('identifier needs to be a str type')

        if isinstance(interaction_type, str):
            self.interaction_type = interaction_type
        else:
            raise TypeError('interaction_type needs to be a str type')

        if isinstance(path, str):
            self.path = path
        else:
            raise TypeError('path needs to be a str type')

        if isinstance(author, str):
            self.author = author
        else:
            raise TypeError('author needs to be a str type')

        self.manifest()

    def manifest(self):
        manifest = \
            Element('manifest',
                    {'xmlns': "http://www.imsglobal.org/xsd/imscp_v1p1",
                     'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
                     'xsi:schemaLocation':
                         "http://www.imsglobal.org/xsd/imscp_v1p1"
                         "http://www.imsglobal.org/xsd/qti/qtiv2p2/qtiv2p2_imscpv1p2_v1p0.xsd"
                         "http://www.imsglobal.org/xsd/imsqti_v2p2"
                         "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_v2p2.xsd"
                         "http://www.imsglobal.org/xsd/imsqti_metadata_v2p2"
                         "http://www.imsglobal.org/xsd/qti/qtiv2p2/imsqti_metadata_v2p2.xsd"
                         "http://ltsc.ieee.org/xsd/LOM"
                         "http://www.imsglobal.org/xsd/imsmd_loose_v1p3p2.xsd",
                     'identifier': 'manifestID'})
        metadata = SubElement(manifest, 'metadata')
        schema = SubElement(metadata, 'schema')
        schema.text = 'QTIv2.2 Package'
        schema_version = SubElement(metadata, 'schemaversion')
        schema_version.text = '1.0.0'
        # organizations
        SubElement(manifest, 'organizations')
        resources = SubElement(manifest, 'resources')
        resource = SubElement(resources, 'resource', {'identifier': self.identifier,
                                                      'type': 'imsqti_item_xmlv2p2',
                                                      'href': self.identifier + '.xml'})
        metadata_resource = SubElement(resource, 'metadata')
        lom = SubElement(metadata_resource, 'lom', {'xmls': "http://ltsc.ieee.org/xsd/LOM"})
        general = SubElement(lom, 'general')
        identifier = SubElement(general, 'identifier')
        entry = SubElement(identifier, 'entry')
        entry.text = 'id' + b2a_hex(urandom(16))
        title = SubElement(general, 'title')
        string = SubElement(title, 'string', {'language': "en"})
        string.text = self.identifier
        life_cycle = SubElement(lom, 'lifeCycle')
        contribute = SubElement(life_cycle, 'contribute')
        date = SubElement(contribute, 'date')
        date_time = SubElement(date, 'dateTime')
        date_time.text = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        role = SubElement(contribute, 'role')
        source = SubElement(role, 'source')
        source.text = 'LOMv1.0'
        value = SubElement(role, 'value')
        value.text = self.author
        entity = SubElement(life_cycle, 'entity')
        entity.text = b2a_hex(urandom(16))
        educational = SubElement(lom, 'educational')
        learning_resource_type = SubElement(educational, 'learningResourceType')
        source = SubElement(learning_resource_type, 'source')
        source.text = 'QTIv2.2'
        value = SubElement(learning_resource_type, 'value')
        value.text = 'AssessmentItem'
        qti_meta_data = SubElement(lom, 'qtiMetaData',
                                   {'xmlns': "http://www.imsglobal.org/xsd/imsqti_metadata_v2p2"})
        interaction_type = SubElement(qti_meta_data, 'interactionType')
        interaction_type.text = self.interaction_type
        # file
        SubElement(resource, 'file', {'href': self.identifier + '.xml'})

        rough_string = tostring(manifest)
        reparsed = parseString(rough_string)

        if not self.path:
            qti_file = open_file('imsmanifest.xml', 'w+', encoding="utf-8")
        else:
            qti_file = open_file(self.path + 'imsmanifest.xml', 'w+', encoding="utf-8")
        qti_file.write(reparsed.toprettyxml(indent="  "))
        qti_file.close()

        self.export()

    def export(self):
        if not self.path:
            zip_file = ZipFile(self.identifier + '.zip', 'w')
            zip_file.write('imsmanifest.xml')
            remove('imsmanifest.xml')
            zip_file.write(self.identifier + '.xml')
            remove(self.identifier + '.xml')
            zip_file.close()
        else:
            zip_file = ZipFile(self.path + self.identifier + '.zip', 'w')
            zip_file.write(self.path + 'imsmanifest.xml', basename(self.path + 'imsmanifest.xml'))
            remove(self.path + 'imsmanifest.xml')
            zip_file.write(self.path + self.identifier + '.xml',
                           basename(self.path + self.identifier + '.xml'))
            remove(self.path + self.identifier + '.xml')
            zip_file.close()
