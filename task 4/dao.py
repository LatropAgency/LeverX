class DAO:
    def __init__(self, connection):
        self.connection = connection
        self._execute_query("create database if not exists leverx", fetch=False)
        self._execute_query("use leverx", fetch=False)

    def insert(self, objects: dict):
        raise NotImplementedError

    def _execute_query(self, query, fetch=True):
        if self.connection.is_connected():
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                if fetch:
                    return cursor.fetchall()


class StudentDAO(DAO):
    def __init__(self, connection):
        super().__init__(connection)
        query = """create table if not exists students (
                    id int not null primary key,
                    name nvarchar(64) not null,
                    room int not null,
                    birthday datetime not null,
                    sex enum("M", "F") not null,
                    foreign key (room) references rooms(id) on delete cascade
                    );"""
        return self._execute_query(query, fetch=False)

    def create_index(self):
        """создание индекса"""
        query = "ALTER TABLE students ADD INDEX (sex)"
        self._execute_query(query, fetch=False)

    def insert(self, students: dict):
        if self.connection.is_connected():
            with self.connection.cursor() as cursor:
                for id, student in students.items():
                    cursor.execute("insert into students values(%s, %s, %s, %s, %s)", (
                        student.id, student.name, student.room, student.birthday, student.sex))
            self.connection.commit()


class RoomDAO(DAO):
    def __init__(self, connection):
        super().__init__(connection)
        query = """create table if not exists rooms (
                 id int not null primary key,
                 name nvarchar(64) not null);"""
        self._execute_query(query, fetch=False)

    def rooms_list_with_student_count(self):
        """список комнат и количество студентов в каждой из них"""
        query = """select rooms.name, count(*)
                    from rooms inner join students
                    on rooms.id = students.room
                    group by rooms.id;"""
        return self._execute_query(query)

    def top_5_rooms_with_min_avg_age_of_students(self):
        """top 5 комнат, где самые маленький средний возраст студентов"""
        query = """select A.name, B.AvgAge
                from rooms as A
                inner join (SELECT room, avg(DATEDIFF(CURRENT_DATE, STR_TO_DATE(t.birthday, '%Y-%m-%d'))/365) as AvgAge
                FROM students as t
                group by room
                order by AvgAge limit 5) as B
                on A.id = B.room;"""
        return self._execute_query(query)

    def top_5_rooms_with_max_students_age_diff(self):
        """top 5 комнат с самой большой разницей в возрасте студентов"""
        query = """select room, (max(AgeInYears)-min(AgeInYears)) as MaxDiffAge 
                from (SELECT room, DATEDIFF(CURRENT_DATE, STR_TO_DATE(t.birthday, '%Y-%m-%d'))/365 as AgeInYears
                FROM students as t) as A 
                group by room 
                order by MaxDiffAge desc 
                limit 5;"""
        return self._execute_query(query)

    def rooms_with_males_and_females(self):
        """список комнат где живут разнополые студенты"""
        query = """select name
                from rooms as A inner join
                (select room, count(sex) as count 
                from (select * from students 
                group by room, sex 
                order by room) as A
                group by room
                having count = 2) as B
                on A.id = B.room;"""
        return self._execute_query(query)

    def insert(self, rooms: dict):
        if self.connection.is_connected():
            with self.connection.cursor() as cursor:
                for id, room in rooms.items():
                    cursor.execute("insert into rooms values(%s, %s)", (room.id, room.name))
            self.connection.commit()
