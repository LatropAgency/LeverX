import json
import argparse
import mysql.connector
from serializers import JsonSerializer, XmlSerializer
from dao import StudentDAO, RoomDAO
from models import Student, Room


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
    parser.add_argument('host', type=str, help='Database host')
    parser.add_argument('user', type=str, help='Username')
    parser.add_argument('password', type=str, help='User Password')
    args = parser.parse_args()
    config = {
        'host': args.host,
        'user': args.user,
        'password': args.password,
    }
    if args.serializer == 'json':
        Room.serializer = JsonSerializer()
    elif args.serializer == 'xml':
        Room.serializer = XmlSerializer()
    rooms = read_objects(args.rooms, Room)
    students = read_objects(args.students, Student)
    join(rooms, students)
    Room.save(rooms.values())
    with mysql.connector.connect(**config) as connection:
        rooms_dao = RoomDAO(connection)
        students_dao = StudentDAO(connection)
        rooms_dao.insert(rooms)
        students_dao.insert(students)
        print(rooms_dao.rooms_list_with_student_count())
        print(rooms_dao.top_5_rooms_with_min_avg_age_of_students())
        print(rooms_dao.top_5_rooms_with_max_students_age_diff())
        print(rooms_dao.rooms_with_males_and_females())
        students_dao.create_index()
