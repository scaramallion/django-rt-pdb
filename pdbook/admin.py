from django.contrib import admin
from django import template
from django.template.context import Context
from django.utils.html import format_html, mark_safe

from pdbook.models import Machine, Beam, Data


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
    list_display = ('visible_name', 'manufacturer', 'model', 'serial_number')
    inlines = [BeamTabular]
    ordering = ('visible_name',)
    exclude = ('slug',)
    fields = ('machine_type', 'manufacturer', 'model', 'serial_number',
              'name', 'visible_name', 'description', 'slug')

    def get_readonly_fields(self, request, obj=None):
        fields = []
        if obj:
            fields += ['slug']

        return fields


class BeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'machine', 'visible_name', 'energy', 'modality')
    inlines = [DataTabular]
    ordering = ('machine', 'modality', 'name',)
    exclude = ('slug',)
    fields = ('machine', 'modality', 'energy', 'name', 'visible_name',
              'description', 'slug')

    def get_readonly_fields(self, request, obj=None):
        fields = []
        if obj:
            fields += ['slug']

        return fields


class DataAdmin(admin.ModelAdmin):
    list_display = ('html_visible_name', 'beam', 'name')
    ordering = ('beam', 'name',)
    exclude = ('slug',)
    fields = ('beam', 'data', 'interpolation_type', 'show_y_values', 'name',
              'visible_name', 'description', 'data_source', 'slug')

    def get_readonly_fields(self, request, obj=None):
        fields = []
        if obj:
            fields += ['slug']

        return fields


admin.site.register(Machine, MachineAdmin)
admin.site.register(Beam, BeamAdmin)
admin.site.register(Data, DataAdmin)

