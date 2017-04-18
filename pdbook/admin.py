from django.contrib import admin
from django import template
from django.template.context import Context
from django.utils.html import format_html, mark_safe

from .models import Machine, Beam, Data


register = template.Library()


class BeamTabular(admin.TabularInline):
    model = Beam
    fields = ('name', 'visible_name', 'energy', 'modality', 'description')
    extra = 0


class DataTabular(admin.TabularInline):
    model = Data
    fields = ('name', 'visible_name', 'data', 'interpolation_type', 'data_source', 'description')
    extra = 0
    ordering = ('name',)


class MachineAdmin(admin.ModelAdmin):
    list_display = ('visible_name', 'manufacturer', 'model', 'serial_number', 'description')
    inlines = [BeamTabular]
    ordering = ('visible_name',)


class BeamAdmin(admin.ModelAdmin):
    fields = ('machine', 'name', 'visible_name', 'energy', 'modality', 'description')
    inlines = [DataTabular]
    ordering = ('machine', 'name',)


class DataAdmin(admin.ModelAdmin):
    list_display = ('beam', 'html_visible_name')
    ordering = ('beam', 'name')


admin.site.register(Machine, MachineAdmin)
admin.site.register(Beam, BeamAdmin)
admin.site.register(Data, DataAdmin)

