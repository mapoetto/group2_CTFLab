# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import User
from .models import Lab
from .models import CyberKillChain

# Register your models here.
admin.site.register(User)
admin.site.register(Lab)
admin.site.register(CyberKillChain)