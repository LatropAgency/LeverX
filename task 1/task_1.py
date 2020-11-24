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
        xml = dicttoxml(obj, custom_root='rooms', attr_type=False, item_func=my_item_func)
        with open('result.xml', 'w') as file:
            file.write(xml.decode('utf-8'))


class Student:
    def __init__(self, id: int, name: str, room: int):
        self.id = id
        self.name = name
        self.room = room


class Room:
    serializer = None
    instances = []

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.students = []
        self.__class__.instances.append(self.__dict__)

    @classmethod
    def save(cls):
        cls.serializer.serialize(cls.instances)

    def add(self, student: Student):
        self.students.append(student.__dict__)


if __name__ == '__main__':
    rooms = {}

    parser = argparse.ArgumentParser()
    parser.add_argument('students', type=str)
    parser.add_argument('rooms', type=str)
    parser.add_argument('serializer', type=str, help='Serializer type')
    args = parser.parse_args()

    if args.serializer == 'json':
        Room.serializer = JsonSerializer()
    elif args.serializer == 'xml':
        Room.serializer = XmlSerializer()

    with open(args.students, 'r') as f:
        objects = json.loads(f.read())
        for room in objects:
            rooms[room['id']] = Room(room['id'], room['name'])

    with open(args.rooms, 'r') as f:
        objects = json.loads(f.read())
        for student in objects:
            rooms.get(student['room']).add(Student(student['id'], student['name'], student['room']))

    Room.save()
