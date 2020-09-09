# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from itertools import chain
from django.core import serializers
from django.forms.models import model_to_dict
from django.core.exceptions import ObjectDoesNotExist

# Create your models here.

def validate_flag(value):
    try:
        value = int(value)
    except ValueError:
        raise ValidationError("Inserire un valore numerico_1")


def to_dict(instance):
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields):
        data[f.name] = f.value_from_object(instance)
    for f in opts.many_to_many:
        data[f.name] = [i.id for i in f.value_from_object(instance)]
    return data

class Notifica(models.Model):
    testo = models.CharField(max_length=120)
    link = models.CharField(max_length=220)
    destinatario = models.CharField(max_length=50) #a chi è destinata la notifica (ID dell'utente - oppure TUTTI)

#Ogni volta che si crea una notifica, si fa il check per vedere se l'id di quella notifica esiste nella tab notifica_vista

class User(AbstractBaseUser):
    nome = models.CharField(max_length=120)
    cognome = models.CharField(max_length=120)
    username = models.CharField(max_length=120, unique=True, error_messages={'unique': ("Username già utilizzato")})
    password = models.CharField(max_length=120)
    professione = models.CharField(max_length=120)
    email = models.EmailField(max_length=120, unique=True, error_messages={'unique': ("Email già utilizzata")})
    data = models.DateTimeField(auto_now=False, auto_now_add=True)
    porta_vpn = models.CharField(max_length=10,default='')
    id_ctfd = models.CharField(max_length=10,default='')

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    NOME_FIELD = 'nome'
    COGNOME_FIELD = 'cognome'
    PASSWORD_FIELD = 'password'
    PROFESSIONE_FIELD = 'professione'
    REQUIRED_FIELDS = ['email','username','nome','cognome','password','professione']

class Notifica_vista(models.Model):
    stato = models.CharField(max_length=120) #vista
    user_id = models.ForeignKey(User, related_name="user_id", default=None, blank=True, null=True, on_delete=models.CASCADE)
    notifica_id = models.ForeignKey(Notifica, related_name="notifica_id", default=None, blank=True, null=True, on_delete=models.CASCADE)


class Tag_Args(models.Model):
    colore = models.CharField(max_length=7, unique=True)# #FF5733
    argomento = models.CharField(max_length=20) # SQL Injection
    spiegazione = models.TextField(default='')

    def __str__(self):
        return self.argomento

class Tag_Level(models.Model):
    colore = models.CharField(max_length=7 , unique=True)# #FF5733
    livello = models.CharField(max_length=20) # Difficile

    def __str__(self):
        return self.livello


class CTFd_configs(models.Model):
    url_API = models.CharField(max_length=220)
    token_API = models.CharField(max_length=64)
    port_API = models.IntegerField(validators=[validate_flag], default=8000)

    def save(self, *args, **kwargs):
        if not self.pk and CTFd_configs.objects.exists():
        # if you'll not check for self.pk 
        # then error will also raised in update of exists model
            raise ValidationError('E\' possibile avere una sola istanza di CTFd_configs')
        return super(CTFd_configs, self).save(*args, **kwargs)



class Lab(models.Model):
    nome = models.CharField(max_length=120)
    sotto_titolo = models.CharField(max_length=120, default='')
    docker_name = models.CharField(max_length=120)
    descrizione = models.TextField()
    documentazione = models.TextField(default='')
    flag = models.CharField(max_length=220, default='')
    categoria = models.CharField("Categoria della challenge",max_length=120, default='')
    valore_flag = models.IntegerField("Punteggio della flag",validators=[validate_flag], default=10) #deve essere numerico
    # cap_add=["NET_ADMIN"], detach=True, ports =ports_dict, name=name_lab, auto_remove=True, network=network_name_user

    NET_ADMIN = 'NET_ADMIN'
    TRUE = 'True'
    FALSE = 'False'

    CAP_CHOICES = [
        (NET_ADMIN, 'Net Admin'),
    ]
    cap_add = models.CharField(
       max_length=32,
       choices=CAP_CHOICES,
       default= NET_ADMIN,
    )

    DETACH_CHOICES = [
        (TRUE, 'True'),
        (FALSE, 'False'),
    ]
    detach = models.CharField(
       max_length=32,
       choices=DETACH_CHOICES,
       default=TRUE,
    )

    AUTO_REMOVE_CHOICES = [
        (TRUE, 'True'),
        (FALSE, 'False'),
    ]
    auto_remove = models.CharField(
       max_length=32,
       choices=AUTO_REMOVE_CHOICES,
       default=TRUE,
    )

    #ARGOMENTI = serializers.serialize('json', app.Tag_Args.objects.all(), fields=('argomento'))

    #d.__setitem__(key, value)

    livello=models.ForeignKey(Tag_Level, related_name="livello_diff", default=None, blank=True, null=True, on_delete=models.CASCADE)

    argomento_1=models.ForeignKey(Tag_Args, related_name="argo1", default=None, blank=True, null=True, on_delete=models.CASCADE)
    argomento_2=models.ForeignKey(Tag_Args, related_name="argo2", default=None, blank=True, null=True, on_delete=models.CASCADE)
    argomento_3=models.ForeignKey(Tag_Args, related_name="argo3", default=None, blank=True, null=True, on_delete=models.CASCADE)
    argomento_4=models.ForeignKey(Tag_Args, related_name="argo4", default=None, blank=True, null=True, on_delete=models.CASCADE)


    def save(self, *args, **kwargs):

        from app.middleware import add_challenge, patch_flag, check_challenges ,patch_challenge
        
        try:
            Lab.objects.get(pk=self.pk)

            lab = Lab.objects.get(pk=self.pk)

            if len(lab.flag) >0: #vuol dire che la flag già c'è

                patch = patch_flag(self.flag,self.nome,self.categoria)
                if patch == True:
                    pass
                elif patch == "challenge non trovata":
                    
                    if add_challenge(self.nome, self.valore_flag, self.categoria, self.flag) == True:
                        pass
                    else:
                        raise ValidationError('Errore dell\' API CTFd, il laboratorio non è stato aggiornato (1)')
                elif patch == "flag non trovata":
                    
                    challenge_id=check_challenges(self.nome,self.categoria)
                    if add_flag(challenge_id, self.flag) == True:
                        pass
                    else:
                        raise ValidationError('Errore dell\' API CTFd, il laboratorio non è stato aggiornato (2)')
                else:
                    raise ValidationError('Il patch della flag non è andato a buon fine (Errore non gestito)')
                
                if lab.valore_flag != self.valore_flag:
                    challenge_id=check_challenges(self.nome,self.categoria)
                    if patch_challenge(challenge_id, self.nome, self.valore_flag, self.categoria) == True:
                        pass
                    else:
                        raise ValidationError('Errore dell\' API CTFd, il laboratorio non è stato aggiornato (3)')


                return super(Lab, self).save(*args, **kwargs)

            else:
                if CTFd_configs.objects.exists():

                    if add_challenge(self.nome, self.valore_flag, self.categoria, self.flag) == True:
                        return super(Lab, self).save(*args, **kwargs)
                    else:
                        raise ValidationError('Errore dell\' API CTFd, il laboratorio non è stato aggiornato ')

                else:
                    raise ValidationError('Inserire la configurazione per contattare l\'API di CTFd')
        except ObjectDoesNotExist:
            raise ValidationError('Questo è un nuovo laboratorio')


        
        # if you'll not check for self.pk 
        # then error will also raised in update of exists model
            raise ValidationError('E\' possibile avere una sola istanza di CyberKillChain')
        return super(CyberKillChain, self).save(*args, **kwargs)

    def __str__(self):
        return self.nome + " - " + self.docker_name

class CyberKillChain(models.Model):
    intro = models.TextField(default='')
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

