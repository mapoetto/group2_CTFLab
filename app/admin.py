# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import User
from .models import Lab
from .models import CyberKillChain
from .models import Tag_Args
from .models import Tag_Level
from .models import CTFd_configs
from .models import Notifica, Notifica_vista, Statistiche
from .models import SSHTunnel_configs

# Register your models here.
admin.site.register(User)
admin.site.register(Lab)
admin.site.register(CyberKillChain)
admin.site.register(Tag_Args)
admin.site.register(Tag_Level)
admin.site.register(CTFd_configs)
admin.site.register(SSHTunnel_configs)
admin.site.register(Notifica)
admin.site.register(Statistiche)
