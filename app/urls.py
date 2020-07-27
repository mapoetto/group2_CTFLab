# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from django.views.generic import DetailView
from app.models import User
from app import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('cyberkillchain.html', views.cyberkillchain, name='cyberkillchain'),
    path('page-user.html', views.page_user, name='page_user'),

    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.
    re_path(r'^core/$', views.core, name='core'),
    re_path(r'^.*\.*', views.pages, name='pages'),

]
