# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse
from django import template
import json
import os

from .models import User
from .models import CyberKillChain
from . import lab_manage as lab_manager

@login_required(login_url="/login/")
def index(request):
    return render(request, "index.html")

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'error-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'error-500.html' )
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def page_user(request):
    context = {}
    print(request.user.id)
    user_me = User.objects.get(pk=request.user.id)

    context = {
        'user_me': user_me,
    }
    html_template = loader.get_template( 'page-user.html' )
    return HttpResponse(html_template.render(context, request))

def cyberkillchain(request):
    context = {}
    cyberkill = CyberKillChain.objects.get(id=1)

    context = {
        'CyberKillChain': cyberkill,
    }
    html_template = loader.get_template( 'cyberkillchain.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def core(request):
    if request.is_ajax():
        POST_VALUES = json.loads(request.POST.get('data'))
        if POST_VALUES["action"] == "start_lab" or POST_VALUES["action"] == "stop_lab":
            message = lab_manager.manage(request)
        else:
            message = "Unknown actions"
    else:
        message = "Not Ajax"

    return HttpResponse(message)
