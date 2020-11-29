import argparse
import json
from serializer import JsonSerializer, XmlSerializer
from dao import StudentDAO, RoomDAO
import mysql.connector


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
        serializer = JsonSerializer()
    elif args.serializer == 'xml':
        serializer = XmlSerializer()
    rooms = get_objects('rooms.json')
    students = get_objects('students.json')
    join(rooms, students)
    serializer.serialize(rooms)
    with mysql.connector.connect(**config) as connection:
        if connection.is_connected():
            rooms_dao = RoomDAO(connection)
            students_dao = StudentDAO(connection)
            rooms_dao.insert(rooms)
            students_dao.insert(students)
            print(rooms_dao.rooms_list_with_student_count())
            print(rooms_dao.top_5_rooms_with_min_avg_age_of_students())
            print(rooms_dao.top_5_rooms_with_max_students_age_diff())
            print(rooms_dao.rooms_with_males_and_females())
            students_dao.create_index()
