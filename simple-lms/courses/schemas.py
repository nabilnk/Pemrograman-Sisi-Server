from ninja import Schema
from pydantic import EmailStr
from typing import List, Optional

class UserOut(Schema):
    id: int
    username: str
    role: str

class RegisterIn(Schema):
    username: str
    password: str
    email: str
    role: str = "student"

class CategoryOut(Schema):
    id: int
    name: str

class CourseOut(Schema):
    id: int
    title: str
    description: str
    instructor: UserOut
    category: CategoryOut

class CourseIn(Schema):
    title: str
    description: str
    category_id: int

class LessonOut(Schema):
    id: int
    title: str
    content: str
    order: int


class EnrollmentOut(Schema):
    id: int
    student_id: int
    course_id: int
    enrolled_at: str


class ProgressOut(Schema):
    id: int
    lesson_id: int
    is_completed: bool


class ProgressUpdateIn(Schema):
    lesson_id: int