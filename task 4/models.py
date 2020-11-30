from dataclasses import dataclass


@dataclass
class Student:
    id: int
    name: str
    room: int
    birthday: str
    sex: str


class Room:
    serializer = None

    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.students = []

    @classmethod
    def save(cls, rooms: list):
        cls.serializer.serialize([room.__dict__ for room in rooms])

    def add(self, student: Student):
        self.students.append(student.__dict__)
