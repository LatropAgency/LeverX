import json
import argparse
from serializers import JsonSerializer, XmlSerializer
from models import Student, Room

serializer_type = {
    'json': JsonSerializer,
    'xml': XmlSerializer,
}

def read_objects(path: str, cls: type) -> dict:
    """read objects from json file"""
    with open(path, 'r') as f:
        students = json.loads(f.read())
        return {student['id']: cls(**student) for student in students}


def join(rooms: dict, students: dict) -> None:
    """join rooms and students dicts"""
    for student in students.values():
        rooms.get(student.room).add(student)


if __name__ == '__main__':
    rooms = {}
    students = {}
    parser = argparse.ArgumentParser()
    parser.add_argument('students', type=str)
    parser.add_argument('rooms', type=str)
    parser.add_argument('serializer', type=str, help='Serializer type')
    args = parser.parse_args()
    Room.serializer = serializer_type[args.serializer]()
    rooms = read_objects(args.rooms, Room)
    students = read_objects(args.students, Student)
    join(rooms, students)
    Room.save(rooms.values())
