from django.contrib import admin

from .models import Student, Teacher, Course, Grade


class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name']
#
# class CourseAdmin(admin.ModelAdmin):
#     list_display = ['department']
#

class GradeAdmin(admin.ModelAdmin):
    list_display = ['score', 'course_id']

admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Course)
admin.site.register(Grade, GradeAdmin)
