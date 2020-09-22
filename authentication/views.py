# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from app.models import User
from django.forms.utils import ErrorList
from django.http import HttpResponse
from .forms import LoginForm, SignUpForm
from app.vpn_manage import check_server_vpn, create_server_vpn
from app.middleware import *
from django.core.exceptions import ObjectDoesNotExist
import threading


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                try:
                    login(request, user)
                    request.session["user_pk"] = user.pk
                
                    if check_userCTFd_exists(user.pk) == False:
                        print("\nL'utente su ctfd non esiste... starto il thread\n")
                        t2 = threading.Thread(target=insert_user,args=[user.pk],daemon=True)
                        t2.start()

                    if check_server_vpn(user.pk) == False:

                        t = threading.Thread(target=create_server_vpn,args=[user.pk],daemon=True)
                        t.start()

                        return redirect("/?VPN_CREATING")

                    return redirect("/?success")
                
                except User.DoesNotExist:
                    #print("Tutto ok sir")
                    return redirect("/admin/")
            else:    
                msg = 'Credenziali Errate'    
        else:
            msg = 'Impossibile validare il form'    

    class Meta:
        model = User

    return render(request, "accounts/login.html", {"form": form, "msg" : msg})

def register_user(request):

    msg     = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            nome = form.cleaned_data.get("nome")
            cognome = form.cleaned_data.get("cognome")
            professione = form.cleaned_data.get("professione")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)

            msg     = 'Utente registrato correttamente'
            success = True
            
            #return redirect("/login/")

        else:
            msg = 'Form non valido'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg" : msg, "success" : success })
