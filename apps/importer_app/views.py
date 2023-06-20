# -*- coding: utf-8 -*-

from io import BytesIO
import pandas as pd

from django.shortcuts import render
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
        self.list_unique_model_fields = []  # fields that must be unique in the model
        self.list_non_null_model_fields = []  # fields that cannot be null in the model
        self.row_with_null_values = None
        self.df_with_no_nulls = None  # Dataframe without invalid values
        self.df_with_uniques_value = None  # Dataframe with no duplicate values violating the unique
        # constraint
        self.number_wrong_rows = None  # rows with null or blank, where the model requires a value
        self.number_invalids_rows = None  # rows with all required fields, but one or more does not
        # meet the type or validation defined in the mode
        self.number_rows_violates_unique_constraint = None
        pandas_comand = {
        }

    # TODO: definir estrtuctura dataframe para cada modelo.
    # TODO : validar la cantidad de header

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
                self.compute_row_with_no_null_values()
                self.compute_rows_with_unique_constraint_in_model()

                # TODO: instance clean

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

        if 'id' in self.list_non_null_model_fields:
            # Remove the 'id' field, because the imported template may not contain the field
            self.list_non_null_model_fields.remove('id')

    def compute_row_with_no_null_values(self):
        """
        Compute all rows that have a null value and are defined as not null by the model
        """
        self.df_with_no_nulls = self.df.dropna(subset=self.list_non_null_model_fields, inplace=False)
        number_rows_df = self.df.shape[0]
        number_rows_df_sanitized = self.df_with_no_nulls.shape[0]
        self.number_wrong_rows = abs(number_rows_df - number_rows_df_sanitized)

    def compute_rows_with_unique_constraint_in_model(self):
        """
         Compute all  dataframes rows  with values that violate unique constraint
        """
        self.df_with_uniques_value = self.df.drop_duplicates(subset=self.list_unique_model_fields, keep='first')
        quantity_rows_df1 = self.df_with_uniques_value.shape[0]
        quantity_rows_df2 = self.df_with_uniques_value.shape[0]
        self.number_rows_violates_unique_constraint = abs(quantity_rows_df1 - quantity_rows_df2)

    def students_importer(self):
        student_validation_fields = self.validate_field_in_model(Student)

    def teachers_importer(self):
        teacher_validation_fields = self.validate_field_in_model(Teacher)

    def grades_importer(self):
        grade_validation_fields = self.validate_field_in_model(Grade)






