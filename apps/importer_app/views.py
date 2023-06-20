# -*- coding: utf-8 -*-

from io import BytesIO
import time
import pandas as pd

from django.shortcuts import render

# from tablib import Dataset
from .admin import StudentResource

from .models import *


from django.views import View
from django.http import HttpResponse


class ImporterView(View):
    template_name = 'import.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.importer_choices = {
            'students_file': self.students_importer,
            'teachers_file': self.teachers_importer,
            'grades_file': self.grades_importer,
        }

        self.selected_importer = None
        self.type_input_file = None
        self.file = None
        self.df = pd.DataFrame()
        self.list_unique_model_fields = []     # fields that must be unique in the model
        self.list_non_null_model_fields = []   # fields that cannot be null in the model
        self.row_with_null_values = None
        self.df_with_nulls = None         # Dataframe wint invalid values


        pandas_comand = {
        }

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        request_file = request.FILES

        if request_file and request_file.keys():
            # identify if the request has a file
            self.selected_importer = list(request_file.keys())[0]

            if self.selected_importer:
                # run the importer according to the uploaded file
                self.importer_choices[self.selected_importer]()
                self.file = request_file[self.selected_importer].read()
                self.type_input_file = request_file[self.selected_importer].content_type
                self.create_dataframe_from_file(request)
                self.compute_null_fields()



                #TODO: df validation
                #blank , null , unique

                #TODO: instance clean


        return render(request, self.template_name)

    def create_dataframe_from_file(self, request):
        """ identify if the type of file is CSV, XLS or XLSX"""
        file_io = BytesIO(self.file)

        if self.type_input_file == 'text/csv':
            self.df = pd.read_csv(file_io)
        elif self.type_input_file == 'application/vnd.ms-excel' or \
                self.type_input_file == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            self.df = pd.read_excel(file_io)
        else:
            # TODO: render template
            return render(request, 'invalid content type')

    def validate_field_in_model(self, model):
        """
        Validate all fields no_null , no_blank and uniques in model
        """
        fields = model._meta.get_fields()
        for field in fields:
            try:
                if not field.null or not field.blank:
                    self.list_non_null_model_fields.append(field.name)
                if field.unique:
                    self.list_unique_model_fields.append(field.name)
            except AttributeError:
                pass

    def compute_row_with_null_values(self):
        """
        Calculate all rows that have a null value and are defined as not null by the model
        """
        self.df_with_nulls = self.df.copy().dropna(subset=self.list_non_null_model_fields)


    def students_importer(self):
        student_validation_fields = self.validate_field_in_model(Student)

    def teachers_importer(self):
        # teacher_validation_fields = self.validate_field_in_model(Teacher)
        pass

    def grades_importer(self):
        # grade_validation_fields = self.validate_field_in_model(Grade)
        pass


# TODO:

def compute_row_errors():
    pass


def compute_invalid_error():
    pass


def clean_data_duplicate():
    pass


def identify_extension(file):
    pass


empty_rows = 0


def validate_field_in_model(model):
    """
    Validate all fields no_null , no_blank and uniques in model
    """
    fields = model._meta.get_fields()
    validation_fields = {'uniques': [], 'no_null': []}

    for field in fields:
        try:
            if not field.null or not field.blank:
                validation_fields['no_null'].append(field.name)
            if field.unique:
                validation_fields['uniques'].append(field.name)
            # type_field = field.get_internal_type()
            # result[field_name] = type_field
        except AttributeError:
            pass

    return validation_fields


def student_importer():
    student_validation_fields = validate_field_in_model(Student)
    pass


def simple_upload(request):
    if request.method == 'POST':
        # person_resource = StudentResource()
        # dataset = Dataset()

        request_file = request.FILES['myfile']
        # TODO: identifi the extension
        student_importer()
        # if request.parse_file_upload():
        #     pass

        # identify_extension()

        file = request_file.read()

    return render(request, 'import.html')


def simple_upload22(request):
    if request.method == 'POST':
        person_resource = StudentResource()
        dataset = Dataset()

        new_persons = request.FILES['myfile']

        imported_data = dataset.load(new_persons.read())
        result = person_resource.import_data(dataset, dry_run=False)  # Test the data import
        row_with_errors = [error[0] for error in result.row_errors() if result.row_errors()]
        if not result.has_errors():
            pass
        person_resource.import_data(dataset, dry_run=False)  # Actually import now

    return render(request, 'import.html')
