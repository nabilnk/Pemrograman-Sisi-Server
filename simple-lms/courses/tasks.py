from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from .models import Course, Enrollment
import csv
import os
import time


def _mongo():
    return settings.MONGO_DB


@shared_task
def send_enrollment_email(user_email, course_name):
    subject = f"Enrollment Berhasil: {course_name}"
    message = f"Anda berhasil terdaftar pada course {course_name}. Selamat belajar!"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=True
    )

    _mongo().activity_logs.insert_one({
        "user_email": user_email,
        "action": "send_enrollment_email",
        "course": course_name,
        "created_at": timezone.now().isoformat(),
    })

    return "Email enrollment diproses"


@shared_task
def generate_certificate(enrollment_id):
    enrollment = Enrollment.objects.select_related('student', 'course').get(id=enrollment_id)

    cert_dir = os.path.join(settings.BASE_DIR, 'generated', 'certificates')
    os.makedirs(cert_dir, exist_ok=True)

    filename = f"certificate_enrollment_{enrollment_id}.txt"
    filepath = os.path.join(cert_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as file:
        file.write("SIMPLE LMS CERTIFICATE\n")
        file.write(f"Student : {enrollment.student.username}\n")
        file.write(f"Course  : {enrollment.course.title}\n")
        file.write(f"Date    : {timezone.now().isoformat()}\n")

    _mongo().activity_logs.insert_one({
        "user": enrollment.student.username,
        "action": "generate_certificate",
        "course_id": enrollment.course_id,
        "certificate_file": filepath,
        "created_at": timezone.now().isoformat(),
    })

    return filepath


@shared_task
def update_course_statistics():
    results = []

    for course in Course.objects.all():
        enrollment_count = Enrollment.objects.filter(course=course).count()

        document = {
            "course_id": course.id,
            "course_title": course.title,
            "enrollment_count": enrollment_count,
            "updated_at": timezone.now().isoformat(),
        }

        _mongo().learning_analytics.update_one(
            {"course_id": course.id},
            {"$set": document},
            upsert=True,
        )

        results.append(document)

    return results


@shared_task
def export_course_report():
    report_dir = os.path.join(settings.BASE_DIR, 'generated', 'reports')
    os.makedirs(report_dir, exist_ok=True)

    filename = f"course_report_{int(time.time())}.csv"
    filepath = os.path.join(report_dir, filename)

    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['course_id', 'title', 'instructor', 'category', 'enrollment_count'])

        for course in Course.objects.select_related('instructor', 'category').all():
            writer.writerow([
                course.id,
                course.title,
                course.instructor.username,
                course.category.name,
                Enrollment.objects.filter(course=course).count(),
            ])

    _mongo().activity_logs.insert_one({
        "action": "export_course_report",
        "file": filepath,
        "created_at": timezone.now().isoformat(),
    })

    return filepath