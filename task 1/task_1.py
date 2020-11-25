import json
from dicttoxml import dicttoxml
import argparse


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
        xml = dicttoxml(obj.values(), custom_root='rooms', attr_type=False, item_func=my_item_func)
        with open('result.xml', 'w') as file:
            file.write(xml.decode('utf-8'))


def get_objects(file_path: str):
    with open(file_path, 'r') as f:
        return {x['id']: x for x in json.loads(f.read())}


def join(rooms: dict, students: dict):
    for id, student in students.items():
        lst = rooms[student['room']].get('students', [])
        if not lst:
            rooms[student['room']]['students'] = lst
        lst.append(student)


if __name__ == '__main__':
    serializer = None
    rooms = {}
    students = {}
    parser = argparse.ArgumentParser()
    parser.add_argument('students', type=str)
    parser.add_argument('rooms', type=str)
    parser.add_argument('serializer', type=str, help='Serializer type')
    args = parser.parse_args()
    if args.serializer == 'json':
        serializer = JsonSerializer()
    elif args.serializer == 'xml':
        serializer = XmlSerializer()
    rooms = get_objects('rooms.json')
    students = get_objects('students.json')
    join(rooms, students)
    serializer.serialize(rooms)
