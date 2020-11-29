import json

from dicttoxml import dicttoxml


class Serializer:
    def serialize(self, obj):
        raise NotImplementedError


class JsonSerializer(Serializer):
    def serialize(self, obj):
        with open('result.json', 'w') as file:
            json.dump(obj, file, indent=4)


class XmlSerializer(Serializer):
    def serialize(self, obj):
        my_item_func = lambda x: 'room'
        xml = dicttoxml(obj, custom_root='rooms', attr_type=False, item_func=my_item_func)
        with open('result.xml', 'w') as file:
            file.write(xml.decode('utf-8'))