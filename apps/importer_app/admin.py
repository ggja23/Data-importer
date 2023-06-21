from django.contrib import admin

from .models import *

class CourseInline(admin.TabularInline):
    model = Course


class TeacherAdmin(admin.ModelAdmin):
    inlines = [CourseInline]


class GradesInline(admin.TabularInline):
    model = Grade
    extra = 0
    min_num = 0


class CourseAdmin(admin.ModelAdmin):
    filter_horizontal = ['student_ids']


class GradeAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'score', 'course_id', 'date']
    # filter_horizontal = ('student_ids',)


class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name']
    inlines = [GradesInline]


admin.site.register(Student, StudentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Grade, GradeAdmin)
