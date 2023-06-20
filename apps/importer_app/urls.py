# -*- coding: utf-8 -*-


from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic.base import RedirectView
from .views import *

urlpatterns = [
    path('', login_required(ImporterView.as_view()), name='upload_file'),
]