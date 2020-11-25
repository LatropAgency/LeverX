import argparse
import json
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


class DAO:
    def __init__(self, connection):
        self.connection = connection
        if self.connection.is_connected():
            self.cursor = connection.cursor()
            self.cursor.execute("create database if not exists leverx")
            self.cursor.execute("use leverx")
            self.cursor.close()

    def insert(self, objects: dict):
        raise NotImplementedError


class StudentDAO(DAO):
    def __init__(self, connection):
        super().__init__(connection)
        if self.connection.is_connected():
            self.cursor = connection.cursor()
            self.cursor.execute("""create table if not exists students (
                                id int not null primary key,
                                name nvarchar(64) not null,
                                room int not null,
                                birthday datetime not null,
                                sex enum("M", "F") not null,
                                foreign key (room) references rooms(id) on delete cascade
                                );""")
            self.cursor.close()

    def create_index(self):
        """создание индекса"""
        if self.connection.is_connected():
            with self.connection.cursor() as cursor:
                cursor.execute("ALTER TABLE students ADD INDEX (sex)")

    def insert(self, students: dict):
        if self.connection.is_connected():
            self.cursor = connection.cursor()
            for id, student in students.items():
                self.cursor.execute("insert into students values(%s, %s, %s, %s, %s)", (
                    student['id'], student['name'], student['room'], student['birthday'], student['sex']))
            self.cursor.close()
            self.connection.commit()


class RoomDAO(DAO):
    def __init__(self, connection):
        super().__init__(connection)
        if self.connection.is_connected():
            self.cursor = connection.cursor()
            self.cursor.execute("""create table if not exists rooms (
                             id int not null primary key,
                             name nvarchar(64) not null
                             );""")
            self.cursor.close()

    def rooms_list_with_student_count(self):
        """список комнат и количество студентов в каждой из них"""
        if self.connection.is_connected():
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "select name, count(*) from (select A.name  from rooms as A inner join students as B on A.id = B.room) as A group by name")
                return cursor.fetchall()

    def top_5_rooms_with_min_avg_age_of_students(self):
        """top 5 комнат, где самые маленький средний возраст студентов"""
        if self.connection.is_connected():
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "select A.name, B.AvgAge from rooms as A inner join (SELECT room, avg(DATEDIFF(CURRENT_DATE, STR_TO_DATE(t.birthday, '%Y-%m-%d'))/365) as AvgAge FROM students as t group by room order by AvgAge limit 5) as B on A.id = B.room")
                return cursor.fetchall()

    def top_5_rooms_with_max_students_age_diff(self):
        """top 5 комнат с самой большой разницей в возрасте студентов"""
        if self.connection.is_connected():
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "select room, (max(AgeInYears)-min(AgeInYears)) as MaxDiffAge from (SELECT room, DATEDIFF(CURRENT_DATE, STR_TO_DATE(t.birthday, '%Y-%m-%d'))/365 as AgeInYears FROM students as t) as A group by room order by MaxDiffAge desc limit 5")
                return cursor.fetchall()

    def rooms_with_males_and_females(self):
        """список комнат где живут разнополые студенты"""
        if self.connection.is_connected():
            with self.connection.cursor() as cursor:
                cursor.execute(
                    "select name from rooms as A inner join (select room, count(sex) as count from (select * from students group by room, sex order by room) as A group by room having count = 2) as B on A.id = B.room")
                return cursor.fetchall()

    def insert(self, rooms: dict):
        if self.connection.is_connected():
            self.cursor = connection.cursor()
            for id, room in rooms.items():
                self.cursor.execute("insert into rooms values(%s, %s)", (room['id'], room['name']))
            self.cursor.close()
            self.connection.commit()


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
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'Vovanu14_',
    }
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
    connection = mysql.connector.connect(**config)
    try:
        if connection.is_connected():
            # cursor = connection.cursor()
            # cursor.execute("create database if not exists leverx")
            rooms_dao = RoomDAO(connection)
            students_dao = StudentDAO(connection)
            # cursor.execute("delete from rooms")  # нужно удалить
            rooms_dao.insert(rooms)
            students_dao.insert(students)
            print(rooms_dao.rooms_list_with_student_count())
            print(rooms_dao.top_5_rooms_with_min_avg_age_of_students())
            print(rooms_dao.top_5_rooms_with_max_students_age_diff())
            print(rooms_dao.rooms_with_males_and_females())
            students_dao.create_index()
            # cursor.execute("use leverx")
            # rooms_table = """create table if not exists rooms (
            #                  id int not null primary key,
            #                  name nvarchar(64) not null
            #                  );"""
            # students_table = """create table if not exists students (
            #                     id int not null primary key,
            #                     name nvarchar(64) not null,
            #                     room int not null,
            #                     birthday datetime not null,
            #                     sex enum("M", "F") not null,
            #                     foreign key (room) references rooms(id) on delete cascade
            #                     );"""
            # cursor.execute(rooms_table)
            # cursor.execute(students_table)
            # for id, room in rooms.items():
            #     cursor.execute("insert into rooms values(%s, %s)", (room['id'], room['name']))
            # for id, student in students.items():
            #     cursor.execute("insert into students values(%s, %s, %s, %s, %s)", (
            #         student['id'], student['name'], student['room'], student['birthday'], student['sex']))
            # connection.commit()
            # print('список комнат и количество студентов в каждой из них')
            # cursor.execute(
            #     "select name, count(*) from (select A.name  from rooms as A inner join students as B on A.id = B.room) as A group by name")
            # for i in cursor.fetchall():
            #     print(f'{i[0]}, Count {i[1]}')
            # print('top 5 комнат, где самые маленький средний возраст студентов')
            # cursor.execute(
            #     "select A.name, B.AvgAge from rooms as A inner join (SELECT room, avg(DATEDIFF(CURRENT_DATE, STR_TO_DATE(t.birthday, '%Y-%m-%d'))/365) as AvgAge FROM students as t group by room order by AvgAge limit 5) as B on A.id = B.room")
            # for i in cursor.fetchall():
            #     print(f'{i[0]}, AvgAge: {i[1]}')
            # print('top 5 комнат с самой большой разницей в возрасте студентов')
            # cursor.execute(
            #     "select room, (max(AgeInYears)-min(AgeInYears)) as MaxDiffAge from (SELECT room, DATEDIFF(CURRENT_DATE, STR_TO_DATE(t.birthday, '%Y-%m-%d'))/365 as AgeInYears FROM students as t) as A group by room order by MaxDiffAge desc limit 5")
            # for i in cursor.fetchall():
            #     print(f'{i[0]}, MaxDiffAge: {i[1]}')
            # print('список комнат где живут разнополые студенты')
            # cursor.execute(
            #     "select name from rooms as A inner join (select room, count(sex) as count from (select * from students group by room, sex order by room) as A group by room having count = 2) as B on A.id = B.room")
            # for i in cursor.fetchall():
            #     print(i[0])
            # print("в результате надо сгенерировать SQL запрос который добавить нужные индексы")
            # with connection.cursor() as cursor:
            #     cursor.execute("ALTER TABLE students ADD INDEX (sex)")
    finally:
        connection.close()
