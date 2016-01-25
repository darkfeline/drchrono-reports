from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = patterns(
    '',
    url(r'^$', login_required(views.index), name='index'),
    url(r'^setup/$', login_required(views.setup), name='setup'),
    url(r'^update/$', login_required(views.update), name='update'),
)
