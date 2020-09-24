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
from django.contrib.auth.models import PermissionsMixin

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
    destinatario = models.CharField(max_length=50, help_text="Inserire l'id dell utente, per mandare singolarmente una notifica a quell'utente, oppure la parola 'tutti' per mandarla a tutti gli utenti") #a chi è destinata la notifica (ID dell'utente - oppure TUTTI)
    class Meta:
        verbose_name = 'Notifiche'
        verbose_name_plural = 'Notifiche'
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
    pwd_ctfd = models.CharField(max_length=120,default='')

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    NOME_FIELD = 'nome'
    COGNOME_FIELD = 'cognome'
    PASSWORD_FIELD = 'password'
    PROFESSIONE_FIELD = 'professione'
    REQUIRED_FIELDS = ['email','username','nome','cognome','password','professione']

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return False

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return False

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class Statistiche(models.Model):
    lab_avviati = models.IntegerField(validators=[validate_flag], default=0)
    flag_trovate = models.IntegerField(validators=[validate_flag], default=0)
    guide_lette = models.IntegerField(validators=[validate_flag], default=0)
    punteggio = models.IntegerField(validators=[validate_flag], default=0)
    user_id = models.ForeignKey(User, related_name="user_id_stat", default=None, blank=True, null=True, on_delete=models.CASCADE)
    class Meta:
        verbose_name = 'Statistiche dell\'utente'
        verbose_name_plural = 'Statistiche dell\'utente'

class Notifica_vista(models.Model):
    stato = models.CharField(max_length=120) #vista
    user_id = models.ForeignKey(User, related_name="user_id", default=None, blank=True, null=True, on_delete=models.CASCADE)
    notifica_id = models.ForeignKey(Notifica, related_name="notifica_id", default=None, blank=True, null=True, on_delete=models.CASCADE)


class Tag_Args(models.Model):
    colore = models.CharField(max_length=7, unique=True, help_text = "Inserire un colore esadecimale, esempio: #DCB50A")# #FF5733
    argomento = models.CharField(max_length=20) # SQL Injection
    spiegazione = models.TextField(default='')

    class Meta:
        verbose_name = 'Argomenti per laboratori'
        verbose_name_plural = 'Argomenti per laboratori'

    def __str__(self):
        return self.argomento

class Tag_Level(models.Model):
    colore = models.CharField(max_length=7 , unique=True, help_text = "Inserire un colore esadecimale, esempio: #DCB50A")# #FF5733
    livello = models.CharField(max_length=20) # Difficile

    class Meta:
        verbose_name = 'Livelli di difficoltà per laboratori'
        verbose_name_plural = 'Livelli di difficoltà per laboratori'

    def __str__(self):
        return self.livello


class CTFd_configs(models.Model):
    url_API = models.CharField(max_length=220)
    token_API = models.CharField(max_length=64)
    port_API = models.IntegerField(validators=[validate_flag], default=8000)

    class Meta:
        verbose_name = 'Configurazione per la connessione CTFd'
        verbose_name_plural = 'Configurazione per la connessione CTFd'

    def save(self, *args, **kwargs):
        if not self.pk and CTFd_configs.objects.exists():
        # if you'll not check for self.pk 
        # then error will also raised in update of exists model
            raise ValidationError('E\' possibile avere una sola istanza di CTFd_configs')
        return super(CTFd_configs, self).save(*args, **kwargs)

class SSHTunnel_configs(models.Model):
    FULL_PATH_SSH_KEY = models.CharField(max_length=220,default='')
    USER_SERVER = models.CharField(max_length=64,default='')
    DNS_NAME_SERVER = models.CharField(max_length=220,default='')
    LOCAL_PORT = models.IntegerField(validators=[validate_flag],default='')
    REMOTE_PORT = models.IntegerField(validators=[validate_flag],default='')
    
    class Meta:
        verbose_name = 'Configurazione per la connessione alla macchina Docker'
        verbose_name_plural = 'Configurazione per la connessione alla macchina Docker'

    def save(self, *args, **kwargs):
        if not self.pk and SSHTunnel_configs.objects.exists():
            raise ValidationError('E\' possibile avere una sola istanza di SSHTunnel_config')
        return super(SSHTunnel_configs, self).save(*args, **kwargs)


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
    hint = models.CharField(max_length=220, default='', blank=True, null=True)
    hint_cost = models.IntegerField("Costo del Hint",validators=[validate_flag], default=4, blank=True, null=True)

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
            #super(Lab, self).save(*args, **kwargs)
            #raise ValidationError('Questo è un nuovo laboratorio')
            pass
            

        return super(Lab, self).save(*args, **kwargs)

    def __str__(self):
        return self.nome + " - " + self.docker_name

    class Meta:
        verbose_name = 'Laboratori'
        verbose_name_plural = 'Laboratori'

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

