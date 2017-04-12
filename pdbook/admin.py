from django.contrib import admin
from django import template
from django.template.context import Context

from .models import Machine, Beam, Data


register = template.Library()


class BeamTabular(admin.TabularInline):
    model = Beam
    fields = ('name', 'visible_name', 'energy', 'modality', 'description')
    extra = 0


class MachineAdmin(admin.ModelAdmin):
    list_display = ('visible_name', 'manufacturer', 'model', 'serial_number', 'description')
    inlines = [BeamTabular]


class DataAdmin(admin.ModelAdmin):
    list_display = ('visible_name', 'beam')


admin.site.register(Machine, MachineAdmin)
admin.site.register(Data, DataAdmin)

