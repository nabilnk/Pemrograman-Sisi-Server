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