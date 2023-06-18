# -*- coding: utf-8 -*-

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from .choices import *


class Person(models.Model):
    """
    Person class model
    """

    first_name = models.CharField(name='First name', max_length=100, null=False)
    last_name = models.CharField(name='Last name', max_length=100, null=False)
    id_number = models.PositiveIntegerField(name='Id number', validators=[MaxValueValidator(9999999999999)], null=False)
    birthdate = models.DateField(name='Birthdate')
    email = models.EmailField(name='Email')
    phone = models.PositiveIntegerField(name='Phone', validators=[MaxValueValidator(999999999999999)])
    gender = models.CharField(name='Gender', choices=GENDER, max_length=1, null=False)

    class Meta:
        abstract = True
        ordering = ['first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Student(Person):
    """
    Student class model
    """

    department = models.CharField(name='Department', max_length=50)
    date_of_admission = models.DateField(name='Date of admission')
    grades_average = models.PositiveIntegerField(name='Grades average', validators=[MaxValueValidator(100)])

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"


class Teacher(Person):
    """
    Teacher class model
    """

    profession = models.CharField(name='Profession', max_length=100)
    years_of_experience = models.PositiveIntegerField(name='Years of experience', validators=[MaxValueValidator(100)])
    department = models.CharField(name='Department', max_length=100)
    institute = models.CharField(name='Institute', max_length=150)
    date_of_hire = models.DateField(name='Date of hire')

    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"


class Course(models.Model):
    """
    Course class model
    """
    name = models.CharField(name='Name', max_length=100, null=False)
    department = models.CharField(name='Department', max_length=100)
    academic_credits = models.PositiveIntegerField(name='Academic credits', validators=[MaxValueValidator(100)])
    start_date = models.DateField(name='Start date')
    end_date = models.DateField(name='End date')
    teacher_id = models.ForeignKey(Teacher, on_delete=models.PROTECT)
    student_ids = models.ManyToManyField(Student)

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

    score = models.PositiveIntegerField(name='Score', validators=[MaxValueValidator(100)])
    date = models.DateField(name='Date')
    student_ids = models.ManyToManyField(Student)
    course_ids = models.ManyToManyField(Course)

    # TODO: score validation < 100 or < 10

    class Meta:
        verbose_name = "Grade"
        verbose_name_plural = "Grades"

    def __str__(self):
        return self.score


