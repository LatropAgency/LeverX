import json
import sys
from dicttoxml import dicttoxml
import mysql.connector


class Serializer:

    def serialize(self, obj):
        raise NotImplementedError


class JsonSerializer(Serializer):

    def serialize(self, obj):
        with open('result.json', 'w') as file:
            json.dump(obj, file, indent=4)


class XmlSerializer(Serializer):

    def serialize(self, obj):
        xml = dicttoxml(obj, custom_root='rooms', attr_type=False, item_func=lambda x: x)
        with open('result.xml', 'w') as file:
            file.write(xml.decode('utf-8'))


class Student:

    def __init__(self, id: int, name: str, room: int, sex: str, birthday: str):
        self.id = id
        self.name = name
        self.room = room
        self.sex = sex
        self.birthday = birthday


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
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Vovanu14_',
    }

    students_file_path, rooms_file_path, serializer_type = sys.argv[1], sys.argv[2], sys.argv[3]

    if serializer_type == 'json':
        Room.serializer = JsonSerializer()
    elif serializer_type == 'xml':
        Room.serializer = XmlSerializer()

    with open(rooms_file_path, 'r') as f:
        objects = json.loads(f.read())
        for room in objects:
            rooms[room['id']] = Room(room['id'], room['name'])

    with open(students_file_path, 'r') as f:
        objects = json.loads(f.read())
        for student in objects:
            rooms.get(student['room']).add(
                Student(student['id'], student['name'], student['room'], student['sex'], student['birthday']))

    connection = mysql.connector.connect(**config)
    try:
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("create database if not exists leverx")
            cursor.execute("use leverx")
            rooms_table = """create table if not exists rooms (
                             id int not null primary key,
                             name nvarchar(64) not null
                             );"""
            students_table = """create table if not exists students (
                                id int not null primary key,
                                name nvarchar(64) not null,
                                room int not null,
                                birthday datetime not null,
                                sex enum("M", "F") not null,
                                foreign key (room) references rooms(id) on delete cascade
                                );"""
            cursor.execute(rooms_table)
            cursor.execute(students_table)
            cursor.execute("delete from rooms")  # нужно удалить
            for id, room in rooms.items():
                cursor.execute("insert into rooms values(%s, %s)", (room.id, room.name))
                for student in room.students:
                    cursor.execute("insert into students values(%s, %s, %s, %s, %s)", (
                        student['id'], student['name'], student['room'], student['birthday'], student['sex']))
            connection.commit()
            print('список комнат и количество студентов в каждой из них')
            cursor.execute(
                "select name, count(*) from (select A.name  from rooms as A inner join students as B on A.id = B.room) as A group by name")
            for i in cursor.fetchall():
                print(f'{i[0]}, Count {i[1]}')
            print('top 5 комнат, где самые маленький средний возраст студентов')
            cursor.execute(
                "select A.name, B.AvgAge from rooms as A inner join (SELECT room, avg(DATEDIFF(CURRENT_DATE, STR_TO_DATE(t.birthday, '%Y-%m-%d'))/365) as AvgAge FROM students as t group by room order by AvgAge limit 5) as B on A.id = B.room")
            for i in cursor.fetchall():
                print(f'{i[0]}, AvgAge: {i[1]}')
            print('top 5 комнат с самой большой разницей в возрасте студентов')
            cursor.execute(
                "select room, (max(AgeInYears)-min(AgeInYears)) as MaxDiffAge from (SELECT room, DATEDIFF(CURRENT_DATE, STR_TO_DATE(t.birthday, '%Y-%m-%d'))/365 as AgeInYears FROM students as t) as A group by room order by MaxDiffAge desc limit 5")
            for i in cursor.fetchall():
                print(f'{i[0]}, MaxDiffAge: {i[1]}')
            print('список комнат где живут разнополые студенты')
            cursor.execute(
                "select name from rooms as A inner join (select room, count(sex) as count from (select * from students group by room, sex order by room) as A group by room having count = 2) as B on A.id = B.room")
            for i in cursor.fetchall():
                print(i[0])
            print("в результате надо сгенерировать SQL запрос который добавить нужные индексы")
            cursor.execute("ALTER TABLE students ADD INDEX (sex)")
    finally:
        connection.close()

    Room.save()
