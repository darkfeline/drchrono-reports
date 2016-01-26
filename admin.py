from __future__ import unicode_literals

from django.contrib import admin

from . import models


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'access_token',
        'refresh_token',
        'expires',
        'last_updated',
    )


class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
    )


class TemplateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'doctor',
        'name',
    )


class FieldAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'template',
        'name',
    )


class ValueAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'field',
        'value',
    )


admin.site.register(models.ReportsUser, UserAdmin)
admin.site.register(models.Doctor, DoctorAdmin)
admin.site.register(models.Template, TemplateAdmin)
admin.site.register(models.Field, FieldAdmin)
admin.site.register(models.Value, ValueAdmin)
