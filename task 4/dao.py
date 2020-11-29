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
            self.cursor = self.connection.cursor()
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
                    "select rooms.name, count(*) from rooms inner join students on rooms.id = students.room group by rooms.id;")
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
            self.cursor = self.connection.cursor()
            for id, room in rooms.items():
                self.cursor.execute("insert into rooms values(%s, %s)", (room['id'], room['name']))
            self.cursor.close()
            self.connection.commit()
