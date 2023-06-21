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
            'students_file': {
                'model': Student,
                'headers': [
                    'first_name',
                    'last_name',
                    'id_number',
                    'birthdate',
                    'email',
                    'phone',
                    'gender',
                    'department',
                    'date_of_admission',
                    'grades_average']
            },
            'teachers_file': {
                'model': Teacher,
                'headers': [
                    'first_name',
                    'last_name',
                    'id_number',
                    'birthdate',
                    'email',
                    'phone',
                    'gender',
                    'profession',
                    'years_of_experience',
                    'department',
                    'institute',
                    'date_of_hire'
                ]
            },
            'grades_file': {
                'model': Grade,
                'headers': [
                    'name',
                    'id_number',
                    'department',
                    'academic_credits',
                    'start_date',
                    # 'teacher_id',
                    # 'student_ids',
                ]
            }
        }

        self.selected_importer = None
        self.input_file_type = None
        self.file = None
        self.model = None
        self.df = pd.DataFrame()
        self.are_the_headers_valid = bool
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

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        context = {}
        request_file = request.FILES

        if request_file and request_file.keys():
            # identify if the request has a file
            self.selected_importer = list(request_file.keys())[0]

            if self.selected_importer:
                # Read the file
                self.file = request_file[self.selected_importer].read()

                # Identify the input file type
                self.input_file_type = request_file[self.selected_importer].content_type

                # identify the model of the uploaded file and calculate what the non-null,
                # non-blank, and unique fields should be
                self.model = self.importer_choices[self.selected_importer]['model']
                self.identify_non_null_non_blank_and_unique_fields(self.model)

                self.create_dataframe_from_file(request)
                self.validate_file_headers()

            if self.are_the_headers_valid:
                self.compute_row_with_no_null_values()
                self.compute_rows_with_unique_constraint_in_model()
                self.save_object_instance_from_df()
                # TODO: instance clean
                # self.df_with_uniques_value

            else:
                context = {
                    'message': 'invalid headers!',
                    'required_headers': self.importer_choices[self.selected_importer]['headers'],
                    'model': self.model._meta.model_name if self.model else False
                }

        return render(request, self.template_name, context=context)

    def create_dataframe_from_file(self, request):
        """ identify if the type of file is CSV, XLS or XLSX"""
        file_io = BytesIO(self.file)

        if self.input_file_type == 'text/csv':
            self.df = pd.read_csv(file_io)
        elif self.input_file_type == 'application/vnd.ms-excel' or \
                self.input_file_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            self.df = pd.read_excel(file_io)
        else:
            # TODO: render template
            return render(request, 'invalid content type')

    def identify_non_null_non_blank_and_unique_fields(self, model):
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

        if 'id' in self.list_unique_model_fields:
            # Remove the 'id' field, because the imported template may not contain the field
            self.list_unique_model_fields.remove('id')

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
        self.df_with_uniques_value = self.df_with_uniques_value.fillna('')

    def validate_file_headers(self):
        file_headers = list(self.df.columns.values)
        required_headers = self.importer_choices[self.selected_importer]['headers']
        self.are_the_headers_valid = file_headers == required_headers


    def save_object_instance_from_df(self):
        data = self.df_with_uniques_value.to_dict(orient='records')

        for element in data:
            try:
                filtered_element = {}
                for key, value in element.items():
                    if value != "":
                        filtered_element[key] = value

                object_instance = self.model(**filtered_element)
                object_instance.save()
            except ValidationError as e:
                pass
