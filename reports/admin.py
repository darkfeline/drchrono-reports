# Copyright (C) 2016  Allen Li
#
# This file is part of drchrono-reports.
#
# drchrono-reports is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# drchrono-reports is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with drchrono-reports.  If not, see <http://www.gnu.org/licenses/>.

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


class UserDoctorAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'doctor',
    )


class TemplateAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'doctor',
        'name',
    )


class UserTemplateAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'template',
    )


class FieldAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'template',
        'name',
    )


class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'doctor',
        'date',
    )


class ValueAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'field',
        'appointment',
    )


admin.site.register(models.ReportsUser, UserAdmin)
admin.site.register(models.Doctor, DoctorAdmin)
admin.site.register(models.UserDoctor, UserDoctorAdmin)
admin.site.register(models.Template, TemplateAdmin)
admin.site.register(models.UserTemplate, UserTemplateAdmin)
admin.site.register(models.Field, FieldAdmin)
admin.site.register(models.Appointment, AppointmentAdmin)
admin.site.register(models.Value, ValueAdmin)
