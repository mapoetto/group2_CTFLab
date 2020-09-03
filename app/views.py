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

from app.setup_docker_client import get_docker_client
from app.setup_docker_client import LOCAL_TUNNEL

import html

from .models import Tag_Level
from .models import Tag_Args
from .models import User
from .models import CyberKillChain
from .models import Lab
from . import lab_manage as lab_manager
from . import user_manage as user_manager
from . import notification_manage as notification_manager

@login_required(login_url="/login/")
def index(request):
    return render(request, "index.html")

@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        print("\n\n\n\n except lastttt1")
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:
        html_template = loader.get_template( 'error-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
        print("\n\n\n\n except lastttt3")
        html_template = loader.get_template( 'error-500.html' )
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def get_client_vpn(request):
    
    client = get_docker_client(LOCAL_TUNNEL)

    user_id = str(request.session["user_pk"])

    cont_vpn = client.containers.get("serverVPN_user_" + user_id)
    stdout = cont_vpn.exec_run(cmd="sh -c 'cat client.ovpn'")

    context = {
        'client': bytes(stdout.output).decode("utf-8"),
    }

    html_template = loader.get_template('client.ovpn')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def argomenti(request):
    context = {}
    page = request.get_full_path()
    pk = page.split("-")
    pk = pk[-1].split(".")
    pk_arg = pk[0]

    arg = Tag_Args.objects.get(pk=pk_arg)

    context = {
        'argomento': arg,
    }
    html_template = loader.get_template( 'argomenti.html' )
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

def doc_lab(request):
    page = request.get_full_path()
    pk = page.split("-")
    pk = pk[-1].split(".")
    pk_arg = pk[0]
    context = {}
    labs = Lab.objects.get(pk=pk_arg)

    context = {
        'labs': labs,
    }

    html_template = loader.get_template( 'documentazione.html' )
    return HttpResponse(html_template.render(context, request))

def esercizi(request):
    context = {}
    labs = Lab.objects.all()
    args = Tag_Args.objects.all()
    livelli = Tag_Level.objects.all()

    client = get_docker_client(LOCAL_TUNNEL)

    user_id = str(request.session["user_pk"])
    try:
        cont_vpn = client.containers.get("serverVPN_user_" + user_id)
        stdout = cont_vpn.exec_run(cmd="sh -c 'cat client.ovpn'")

        if "BEGIN PRIVATE KEY" in bytes(stdout.output).decode("utf-8"):
            vpn_status = "on"
        else:
            vpn_status = "off"
    except:
        vpn_status = "off"

    context = {
        'labs': labs,
        'args': args,
        'livelli': livelli,
        'VPN': vpn_status,
    }



    html_template = loader.get_template( 'esercizi.html' )
    return HttpResponse(html_template.render(context, request))

def cyberkillchain(request):
    context = {}
    cyberkill = CyberKillChain.objects.get(id=1)

    context = {
        'CyberKillChain': cyberkill,
    }
    html_template = loader.get_template( 'cyberkillchain.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login")
def core(request):
    if request.is_ajax():
        POST_VALUES = json.loads(request.POST.get('data'))
        if POST_VALUES["action"] == "start_lab" or POST_VALUES["action"] == "stop_lab":
            message = lab_manager.manage(request)
        elif POST_VALUES["action"] == "get_notifications":
            message = notification_manager.manage(request)
        else:
            message = "Unknown actions"
    else:
        message = "Not Ajax"

    return HttpResponse(message)

@login_required(login_url="/login")
def core_user(request):
    if request.is_ajax():
        message = user_manager.manage(request)
    else:
        message = "Not Ajax"

    return HttpResponse(message)
