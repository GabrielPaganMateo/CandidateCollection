from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Candidate)
admin.site.register(Opening)