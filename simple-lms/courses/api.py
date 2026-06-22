from typing import List

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from celery.result import AsyncResult

from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_extra import NinjaExtraAPI

from .models import (
    Category,
    Course,
    Enrollment,
    Lesson,
    Progress,
)

from .schemas import (
    CategoryOut,
    CourseIn,
    CourseOut,
    RegisterIn,
    UserOut,
    LessonOut,
    ProgressOut,
    ProgressUpdateIn,
)

from .tasks import (
    export_course_report,
    generate_certificate,
    send_enrollment_email,
    update_course_statistics,
)

User = get_user_model()

api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR', 'unknown')


def check_rate_limit(request, limit=60, window=60):
    ip = get_client_ip(request)
    cache_key = f"rate_limit:{ip}"

    current = cache.get(cache_key, 0)

    if current >= limit:
        return False

    if current == 0:
        cache.set(cache_key, 1, timeout=window)
    else:
        cache.incr(cache_key)

    return True


def log_activity(request, action, metadata=None):
    metadata = metadata or {}

    username = 'anonymous'
    if getattr(request, 'user', None) and request.user.is_authenticated:
        username = request.user.username

    settings.MONGO_DB.activity_logs.insert_one({
        "user": username,
        "action": action,
        "metadata": metadata,
        "created_at": timezone.now().isoformat(),
    })


@api.post('/auth/register', response=UserOut, tags=['Auth'])
def register(request, data: RegisterIn):
    if User.objects.filter(username=data.username).exists():
        return api.create_response(
            request,
            {"detail": "Username sudah digunakan."},
            status=400
        )

    if User.objects.filter(email=data.email).exists():
        return api.create_response(
            request,
            {"detail": "Email sudah digunakan."},
            status=400
        )

    user = User.objects.create_user(
        username=data.username,
        password=data.password,
        email=data.email,
        role=data.role,
    )

    log_activity(request, 'register_user', {
        "username": user.username,
        "role": user.role
    })

    return user


@api.get('/auth/me', response=UserOut, auth=JWTAuth(), tags=['Auth'])
def me(request):
    return request.user

@api.get('/categories', response=List[CategoryOut], tags=['Categories'])
def list_categories(request):
    return list(Category.objects.all())

@api.get('/courses', response=List[CourseOut], tags=['Courses'])
def list_courses(request):
    if not check_rate_limit(request):
        return api.create_response(
            request,
            {"detail": "Rate limit exceeded. Maksimal 60 request per menit."},
            status=429
        )

    cache_key = 'courses:list'
    cached_courses = cache.get(cache_key)

    if cached_courses is not None:
        log_activity(request, 'view_course_list_cached')
        return cached_courses

    courses = list(Course.objects.select_related('instructor', 'category').all())

    cache.set(cache_key, courses, timeout=600)

    log_activity(request, 'view_course_list')

    return courses


@api.get('/courses/{course_id}', response=CourseOut, tags=['Courses'])
def course_detail(request, course_id: int):
    if not check_rate_limit(request):
        return api.create_response(
            request,
            {"detail": "Rate limit exceeded. Maksimal 60 request per menit."},
            status=429
        )

    cache_key = f'courses:detail:{course_id}'
    cached_course = cache.get(cache_key)

    if cached_course is not None:
        log_activity(request, 'view_course_detail_cached', {
            "course_id": course_id
        })
        return cached_course

    course = get_object_or_404(
        Course.objects.select_related('instructor', 'category'),
        id=course_id
    )

    cache.set(cache_key, course, timeout=600)

    log_activity(request, 'view_course_detail', {
        "course_id": course_id
    })

    return course


@api.post('/courses', response=CourseOut, auth=JWTAuth(), tags=['Courses'])
def create_course(request, data: CourseIn):
    if request.user.role != 'instructor':
        return api.create_response(
            request,
            {"detail": "Hanya instructor yang diizinkan membuat course."},
            status=403
        )

    category = get_object_or_404(Category, id=data.category_id)

    course = Course.objects.create(
        title=data.title,
        description=data.description,
        instructor=request.user,
        category=category,
    )

    cache.delete('courses:list')

    log_activity(request, 'create_course', {
        "course_id": course.id,
        "title": course.title
    })

    return course


@api.post('/enrollments/{course_id}', auth=JWTAuth(), tags=['Enrollments'])
def enroll_course(request, course_id: int):
    if request.user.role != 'student':
        return api.create_response(
            request,
            {"detail": "Hanya student yang bisa daftar course."},
            status=403
        )

    course = get_object_or_404(Course, id=course_id)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course
    )

    if created:
        send_enrollment_email.delay(request.user.email, course.title)
        update_course_statistics.delay()

        log_activity(request, 'enroll_course', {
            "course_id": course.id,
            "enrollment_id": enrollment.id
        })

    return {
        "message": "Berhasil daftar course" if created else "Student sudah terdaftar pada course ini",
        "enrollment_id": enrollment.id,
    }


@api.post('/enrollments/{enrollment_id}/complete', auth=JWTAuth(), tags=['Enrollments'])
def complete_course(request, enrollment_id: int):
    enrollment = get_object_or_404(
        Enrollment,
        id=enrollment_id,
        student=request.user
    )

    generate_certificate.delay(enrollment.id)

    log_activity(request, 'complete_course', {
        "enrollment_id": enrollment.id,
        "course_id": enrollment.course_id
    })

    return {
        "message": "Course selesai. Certificate sedang dibuat di background."
    }


@api.post('/reports/courses/export', auth=JWTAuth(), tags=['Reports'])
def request_course_report(request):
    if request.user.role != 'admin':
        return api.create_response(
            request,
            {"detail": "Hanya admin yang bisa export report."},
            status=403
        )

    task = export_course_report.delay()

    log_activity(request, 'request_course_report', {
        "task_id": task.id
    })

    return {
        "message": "Report sedang dibuat secara asynchronous.",
        "task_id": task.id
    }


@api.get('/reports/course-statistics', auth=JWTAuth(), tags=['Reports'])
def course_statistics(request):
    if request.user.role != 'admin':
        return api.create_response(
            request,
            {"detail": "Hanya admin yang bisa melihat analytics."},
            status=403
        )

    pipeline = [
        {"$sort": {"enrollment_count": -1}},
        {
            "$project": {
                "_id": 0,
                "course_id": 1,
                "course_title": 1,
                "enrollment_count": 1,
                "updated_at": 1
            }
        },
    ]

    data = list(settings.MONGO_DB.learning_analytics.aggregate(pipeline))

    return {
        "data": data
    }


@api.post('/tasks/update-course-statistics', auth=JWTAuth(), tags=['Tasks'])
def run_update_course_statistics(request):
    if request.user.role != 'admin':
        return api.create_response(
            request,
            {"detail": "Hanya admin yang bisa menjalankan task ini."},
            status=403
        )

    task = update_course_statistics.delay()

    return {
        "message": "Task update course statistics dijalankan.",
        "task_id": task.id
    }

@api.get(
    "/courses/{course_id}/lessons",
    response=List[LessonOut],
    tags=["Lessons"]
)
def course_lessons(request, course_id: int):

    course = get_object_or_404(Course, id=course_id)

    return list(
        Lesson.objects.filter(course=course)
        .order_by("order")
    )

@api.post(
    "/progress/complete",
    response=dict,
    auth=JWTAuth(),
    tags=["Progress"]
)
def complete_lesson(request, data: ProgressUpdateIn):

    lesson = get_object_or_404(
        Lesson,
        id=data.lesson_id
    )

    enrollment = Enrollment.objects.filter(
        student=request.user,
        course=lesson.course
    ).first()

    if not enrollment:
        return api.create_response(
            request,
            {"detail": "Anda belum terdaftar pada course ini."},
            status=403
        )

    progress, created = Progress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson
    )

    progress.is_completed = True
    progress.save()

    log_activity(request, "complete_lesson", {
        "lesson_id": lesson.id,
        "course_id": lesson.course.id
    })

    return {
        "message": "Lesson berhasil diselesaikan"
    }

@api.get(
    "/my-progress",
    auth=JWTAuth(),
    tags=["Progress"]
)
def my_progress(request):

    progress = Progress.objects.filter(
        enrollment__student=request.user
    ).select_related(
        "lesson",
        "enrollment",
        "enrollment__course"
    )

    return [
        {
            "course": p.enrollment.course.title,
            "lesson": p.lesson.title,
            "completed": p.is_completed
        }
        for p in progress
    ]

@api.get(
    "/tasks/{task_id}/status",
    auth=JWTAuth(),
    tags=["Tasks"]
)
def task_status(request, task_id: str):

    task = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": task.status,
        "ready": task.ready(),
        "successful": task.successful() if task.ready() else False,
    }

    if task.ready():
        if task.successful():
            response["result"] = task.result
        else:
            response["error"] = str(task.result)

    return response

@api.get(
    "/activity-logs",
    auth=JWTAuth(),
    tags=["Analytics"]
)
def activity_logs(request):

    if request.user.role != "admin":
        return api.create_response(
            request,
            {"detail": "Hanya admin yang bisa melihat activity logs."},
            status=403
        )

    logs = list(
        settings.MONGO_DB.activity_logs
        .find({}, {"_id": 0})
        .sort("created_at", -1)
        .limit(50)
    )

    return {
        "data": logs
    }

@api.get(
    "/my-enrollments",
    auth=JWTAuth(),
    tags=["Enrollments"]
)
def my_enrollments(request):
    enrollments = Enrollment.objects.filter(
        student=request.user
    ).select_related("course")

    return [
        {
            "id": enrollment.id,
            "course_id": enrollment.course.id,
            "course_title": enrollment.course.title,
            "enrolled_at": enrollment.enrolled_at
        }
        for enrollment in enrollments
    ]