# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError

# Create your models here.

class User(AbstractBaseUser):
    nome = models.CharField(max_length=120)
    cognome = models.CharField(max_length=120)
    username = models.CharField(max_length=120, unique=True, error_messages={'unique': ("Username già utilizzato")})
    password = models.CharField(max_length=120)
    professione = models.CharField(max_length=120)
    email = models.EmailField(max_length=120, unique=True, error_messages={'unique': ("Email già utilizzata")})
    data = models.DateTimeField(auto_now=False, auto_now_add=True)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    NOME_FIELD = 'nome'
    COGNOME_FIELD = 'cognome'
    PASSWORD_FIELD = 'password'
    PROFESSIONE_FIELD = 'professione'
    REQUIRED_FIELDS = ['email','username','nome','cognome','password','professione']

class Lab(models.Model):
    nome = models.CharField(max_length=120)
    sotto_titolo = models.CharField(max_length=120)
    docker_name = models.CharField(max_length=120)
    descrizione = models.TextField()
    dockerfile = models.TextField()

    def __str__(self):
        return self.nome + " - " + self.docker_name

class CyberKillChain(models.Model):
    recon = models.TextField()
    weapon = models.TextField()
    delivery = models.TextField()
    exploitation  = models.TextField()
    installation = models.TextField()
    command_and_control = models.TextField()
    exfiltration = models.TextField()

    def save(self, *args, **kwargs):
        if not self.pk and CyberKillChain.objects.exists():
        # if you'll not check for self.pk 
        # then error will also raised in update of exists model
            raise ValidationError('E\' possibile avere una sola istanza di CyberKillChain')
        return super(CyberKillChain, self).save(*args, **kwargs)

    def __str__(self):
        return "Cyber Kill Chain Spiegazione"

