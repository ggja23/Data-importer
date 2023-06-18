# -*- coding: utf-8 -*-
from datetime import date

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from .choices import *


class Person(models.Model):
    """
    Abstract class : Person model
    """

    first_name = models.CharField('First name', max_length=100, null=False)
    last_name = models.CharField('Last name', max_length=100, null=False)
    id_number = models.PositiveIntegerField('Id number', validators=[MaxValueValidator(9999999999999)], null=False)
    birthdate = models.DateField('Birthdate', validators=[MaxValueValidator(limit_value=date.today)], null=True)
    email = models.EmailField('Email', blank=True)
    phone = models.PositiveIntegerField('Phone', validators=[MaxValueValidator(999999999999999)], blank=True, null=True)
    gender = models.CharField('Gender', choices=GENDER, max_length=1, null=False)

    class Meta:
        abstract = True
        ordering = ['first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Student(Person):
    """
    Student class model
    """

    department = models.CharField('Department', max_length=50, blank=True)
    date_of_admission = models.DateField('Date of admission', null=True, blank=True)
    grades_average = models.PositiveIntegerField('Grades average', validators=[MaxValueValidator(100)], blank=True, null=True)

    # TODO: compute grades_average
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"


class Teacher(Person):
    """
    Teacher class model
    """

    profession = models.CharField('Profession', max_length=100, blank=True, null=True)
    years_of_experience = models.PositiveIntegerField('Years of experience', validators=[MaxValueValidator(100)], blank=True, null=True)
    department = models.CharField('Department', max_length=100, blank=True)
    institute = models.CharField('Institute', max_length=150, blank=True)
    date_of_hire = models.DateField('Date of hire', null=True, blank=True)

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"
        abstract = False


class Course(models.Model):
    """
    Course class model
    """
    name = models.CharField('Name', max_length=100, null=False)
    department = models.CharField('Department', max_length=100, blank=True)
    academic_credits = models.PositiveIntegerField('Academic credits', validators=[MaxValueValidator(100)])
    start_date = models.DateField('Start date', blank=True, null=True)
    end_date = models.DateField('End date', blank=True, null=True)
    teacher_id = models.ForeignKey(Teacher, on_delete=models.PROTECT, blank=True, null=True)
    student_ids = models.ManyToManyField(Student, blank=True)

    # TODO: validation start date < end_date
    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.name


class Grade(models.Model):
    """
    Grade class model
    """

    score = models.PositiveIntegerField('Score', validators=[MaxValueValidator(100)], null=False)
    course_id = models.ForeignKey(Course, on_delete=models.PROTECT, null=False)
    date = models.DateField("Date", auto_now_add=True)
    student_ids = models.ManyToManyField(Student, blank=True)

    # TODO: score validation < 100 or < 10

    class Meta:
        verbose_name = "Grade"
        verbose_name_plural = "Grades"

    def __str__(self):
        return "{}".format(self.score)
        return self.score

# class GradeCourse(models.Model):
#     """
#     Intermediate model to relate the Note with the Course of each student
#     """
#     grade_id = models.ForeignKey(Grade, on_delete=models.PROTECT, null=False)
