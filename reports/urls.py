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

from functools import partial

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = patterns(
    '',
    url(r'^$', login_required(views.index), name='index'),
    url(r'^update/$', login_required(views.update), name='update'),
    url(r'^view_report/$', login_required(views.view_report),
        name='view_report'),
    url(r'^pre_report_archived/$',
        login_required(views.pre_report_archived),
        name='pre_report_archived'),
    url(r'^view_report_archived/$',
        login_required(partial(views.view_report, archived=True)),
        name='view_report_archived'),
    url(r'^ajax/template_fields/$', login_required(views.template_fields),
        name='template_fields'),
    url(r'^dynamic_fields.js$', login_required(views.dynamic_fields),
        name='dynamic_fields.js'),
    url(r'^oauth/$', login_required(views.oauth), name='oauth'),
    url(r'^auth_return/$', login_required(views.auth_return),
        name='auth_return'),
)
