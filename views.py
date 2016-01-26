from __future__ import unicode_literals

import datetime

from django.shortcuts import render
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core import urlresolvers

import pytz
import requests

from .models import ReportsUser
from .models import Template
from .models import Field
from .models import Value

from . import oauthlib


class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303


def _get_oauth_values():
    return {
        'client_id': 'GcFaMT8rcTQW1VWIMPWiKwt5T1APHP2u0mmQleyP',
        'client_secret': 'X368VErNf1dVG2LSrI5zCbATokpvTzg8V2gULhylt8PZrpE7su9hsmOiIiHQgQsG8MeHzK1t1i60fkVKRBv83wP6tgA39ALpPyAk1TV2LwLYcWYvcPBg1iyog4D7ta7f',
        'scope': 'patients user',
        'redirect_uri': 'http://localhost:8001/reports/auth_return/',
    }


def index(request):
    """Handle main page."""
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    try:
        user = ReportsUser.objects.get(user=request.user)
    except ReportsUser.DoesNotExist:
        user = ReportsUser(user=request.user)
        user.save()
    if user.last_updated:
        last_updated_text = 'Last updated on {0:%x} at {0:%X}.'
        last_updated_text = last_updated_text.format(user.last_updated)
    else:
        last_updated_text = 'Not updated.'
    context = {
        'user': user.user,
        'last_updated': last_updated_text,
    }
    return render(request, 'reports/index.html', context)


def update(request):
    """Update data from drchrono."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    user = ReportsUser.objects.get(user=request.user)
    now = datetime.datetime.now(pytz.utc)

    # Refresh if needed.
    if user.expires - datetime.timedelta(minutes=10) < now:
        user.refresh()

    headers = user.auth_header()

    # Update doctors.
    url = oauthlib.url('/api/doctors')
    while url:
        data = requests.get(url, headers=headers).json()
        Doctor.objects.bulk_create(
            Doctor(user=user,
                   id=entry['id'],
                   first_name=entry['first_name'],
                   last_name=entry['last_name'])
            for entry in data['results']
        )
        url = data['next']

    # Update templates.
    url = oauthlib.url('/api/clinical_note_templates')
    while url:
        data = requests.get(url, headers=headers).json()
        Template.objects.bulk_create(
            Template(user=user,
                     id=entry['id'],
                     doctor=Doctor.objects.get(entry['doctor']),
                     name=entry['name'])
            for entry in data['results']
        )
        url = data['next']

    # Update fields.
    url = oauthlib.url('/api/clinical_note_field_types')
    while url:
        data = requests.get(url, headers=headers).json()
        Field.objects.bulk_create(
            Field(user=user,
                  id=entry['id'],
                  template=Template.objects.get(entry['clinical_note_template']),
                  name=entry['name'])
            for entry in data['results']
        )
        url = data['next']

    # Update values.
    url = oauthlib.url('/api/clinical_note_field_values')
    while url:
        data = requests.get(url, headers=headers).json()
        Field.objects.bulk_create(
            Field(user=user,
                  id=entry['id'],
                  field=Field.objects.get(entry['clinical_note_field']),
                  value=entry['value'])
            for entry in data['results']
        )
        url = data['next']


    user.last_updated = now
    user.save()

    index_uri = urlresolvers.reverse('reports:index')
    return HttpResponseSeeOther(index_uri)


def oauth(request):
    """Handle requests to use OAuth."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    vals = _get_oauth_values()
    auth_uri = oauthlib.make_redirect(vals['redirect_uri'],
                                   vals['client_id'],
                                   vals['scope'])
    return HttpResponseSeeOther(auth_uri)


def auth_return(request):
    """Handle OAuth return."""
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    if 'error' in request.GET:
        return HttpResponseForbidden

    vals = _get_oauth_values()

    response = requests.post(oauthlib.TOKEN_URL, data={
        'code': request.GET['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': vals['redirect_uri'],
        'client_id': vals['client_id'],
        'client_secret': vals['client_secret'],
    })
    response.raise_for_status()
    data = response.json()

    access_token = data['access_token']
    refresh_token = data['refresh_token']
    expires_timestamp = datetime.datetime.now(pytz.utc) + \
                        datetime.timedelta(seconds=data['expires_in'])

    user = ReportsUser(user=request.user, access_token=access_token,
                refresh_token=refresh_token, expires=expires_timestamp)
    user.save()

    index_uri = urlresolvers.reverse('reports:index')
    return HttpResponseSeeOther(index_uri)
