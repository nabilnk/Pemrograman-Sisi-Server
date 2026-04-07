from django.contrib import admin
from .models import User, Category, Course, Lesson, Enrollment, Progress

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('category', 'instructor')
    inlines = [LessonInline]

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course',)

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Lesson)
admin.site.register(Progress)