from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.authentication import JWTAuth
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Course, Enrollment, Category
from .schemas import UserOut, RegisterIn, CourseOut, CourseIn
from typing import List

User = get_user_model()
api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)

# --- AUTH ---
@api.post("/auth/register", response=UserOut, tags=["Auth"])
def register(request, data: RegisterIn):
    user = User.objects.create_user(**data.dict())
    return user

@api.get("/auth/me", response=UserOut, auth=JWTAuth(), tags=["Auth"])
def me(request):
    return request.user

# --- COURSES ---
@api.get("/courses", response=List[CourseOut], tags=["Courses"])
def list_courses(request):
    return Course.objects.select_related('instructor', 'category').all()

@api.post("/courses", response=CourseOut, auth=JWTAuth(), tags=["Courses"])
def create_course(request, data: CourseIn):
    if request.user.role != 'instructor':
        return api.create_response(request, {"detail": "Hanya Instructor yang diizinkan"}, status=403)
    
    category = get_object_or_404(Category, id=data.category_id)
    course = Course.objects.create(
        title=data.title,
        description=data.description,
        instructor=request.user,
        category=category
    )
    return course

# --- ENROLLMENTS ---
@api.post("/enrollments/{course_id}", auth=JWTAuth(), tags=["Enrollments"])
def enroll_course(request, course_id: int):
    if request.user.role != 'student':
        return api.create_response(request, {"detail": "Hanya Student yang bisa daftar"}, status=403)
    
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
    return {"message": "Berhasil daftar", "enrollment_id": enrollment.id}