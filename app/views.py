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
from app.config_const import *

import html

from .models import Tag_Level
from .models import Tag_Args
from .models import User, Statistiche
from .models import CyberKillChain
from .models import Lab
from . import lab_manage as lab_manager
from . import user_manage as user_manager
from . import notification_manage as notification_manager
from django.core.exceptions import ObjectDoesNotExist
from threading import Timer
from time import sleep

@login_required(login_url="/login/")
def index(request):

    try:
        me = User.objects.get(pk=request.session["user_pk"])
    except:
        html_template = loader.get_template( 'error-403.html' )
        context = {}
        return HttpResponse(html_template.render(context, request))

    context = {"nome": str(me.nome).title()}

    #def hello(arg1,arg2):
    #    print ("\n\n-------------->hello, world ->"+arg1+" - "+arg2)

    #print("\n\n\nstarto il thread")
    #t = Timer(2.0, hello, ["ciaone11","ciaone22"])
    #t.start()  # after 30 seconds, "hello, world" will be printed
    #print("aspetto 2 secondi ")
    #sleep(10)
    #t.cancel()
    #print("l'ho cancellato")

    html_template = loader.get_template( 'index.html' )
    return HttpResponse(html_template.render(context, request))
    #return render(request, "index.html")

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
    try:
        user_id = str(request.session["user_pk"])
    except:
        html_template = loader.get_template( 'error-403.html' )
        context = {}
        return HttpResponse(html_template.render(context, request))

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

    try:
        my_stats = Statistiche.objects.get(user_id=User.objects.get(pk=request.session["user_pk"]))
        my_stats.guide_lette = int(my_stats.guide_lette) + 1
        my_stats.save()
    except ObjectDoesNotExist:
        my_stats = Statistiche(lab_avviati=0,flag_trovate=0,guide_lette=1,punteggio=0,user_id=User.objects.get(pk=request.session["user_pk"]))
        my_stats.save()

    context = {
        'argomento': arg,
    }
    html_template = loader.get_template( 'argomenti.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def page_user(request):
    context = {}
    #print(request.user.id)
    try:
        user_me = User.objects.get(pk=request.session["user_pk"])
        if user_me.is_superuser == False:
            pass
        else:
            return redirect("/admin/")
        context = {
            'user_me': user_me,
        }
        html_template = loader.get_template( 'page-user.html' )
        return HttpResponse(html_template.render(context, request))
    except User.DoesNotExist:
        #Loggando come admin e visualizzando la dashboard con questo try-except se si clicca su profilo ti ritorna al pannello admin 
        # Da modficiare il ritorno se si vuole, ma non omettere perchè genera l'eccezione
        return redirect("/admin/")
    except KeyError:
        return redirect("/admin/")

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

    #request.session[name_lab]
    #request.session[name_lab+"_start_time"]
    #request.session[name_lab+"_IP"]

    try:
        user_id = str(request.session["user_pk"])
    except:
        html_template = loader.get_template( 'error-403.html' )
        context = {}
        return HttpResponse(html_template.render(context, request))

    from .lab_manage import check_if_container_up

    for lab in labs:
        name_lab = "labid_" + str(lab.pk) + "_userid_" + str(request.session["user_pk"])
        if name_lab in request.session:
            if check_if_container_up(name_lab) == False:
                print("\nHo trovato una sessione settata, per un laboratorio inesistente...provvedo a cancellare:\n")
                try:
                    del request.session[name_lab]
                    del request.session[name_lab+"_start_time"]
                    del request.session[name_lab+"_IP"]
                    print("---Sessioni cancellate")
                except:
                    print("---Errore nel cancellare le sessioni associate")

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

    from .middleware import get_stats
    try:
        user_id = str(request.session["user_pk"])

        if request.is_ajax():
            POST_VALUES = json.loads(request.POST.get('data'))
            if POST_VALUES["action"] == "start_lab" or POST_VALUES["action"] == "stop_lab":
                message = lab_manager.manage(request)
            elif POST_VALUES["action"] == "get_notifications":
                message = notification_manager.manage(request)
            elif POST_VALUES["action"] == "retrive_stats":
                message = get_stats(str(request.session["user_pk"]))
            else:
                message = "Unknown actions"
        else:
            message = "Not Ajax"
    except:
        message = "Eccezione Generata, se sei admin, non puoi lanciare i laboratori!"

    return HttpResponse(message)

@login_required(login_url="/login")
def core_user(request):
    if request.is_ajax():
        message = user_manager.manage(request)
    else:
        message = "Not Ajax"

    return HttpResponse(message)
