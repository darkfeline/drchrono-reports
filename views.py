from __future__ import unicode_literals

import urllib
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
from .models import Values

# _OAUTH_URLS = {
#     'auth': "https://drchrono.com/o/authorize/",
#     'token': "https://drchrono.com/o/token/",
#     'revoke': "https://drchrono.com/o/revoke_token/",
# }

_OAUTH_URLS = {
    'auth': "http://drchrono.dev/o/authorize/",
    'token': "http://drchrono.dev/o/token/",
    'revoke': "http://drchrono.dev/o/revoke_token/",
}


class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303


def _get_oauth_values():
    return {
        'client_id': 'GcFaMT8rcTQW1VWIMPWiKwt5T1APHP2u0mmQleyP',
        'client_secret': 'X368VErNf1dVG2LSrI5zCbATokpvTzg8V2gULhylt8PZrpE7su9hsmOiIiHQgQsG8MeHzK1t1i60fkVKRBv83wP6tgA39ALpPyAk1TV2LwLYcWYvcPBg1iyog4D7ta7f',
        'scope': 'patients user',
        'redirect_uri': 'http://localhost:8001/reports/auth_return/',
    }


def _make_redirect(redirect_uri, client_id, scope):
    return ''.join((
        _OAUTH_URLS['auth'],
        "?redirect_uri={}",
        "&response_type=code",
        "&client_id={}",
        "&scope={}",
    )).format(
        urllib.quote_plus(redirect_uri),
        urllib.quote_plus(client_id),
        urllib.quote_plus(scope),
    )


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

    index_uri = urlresolvers.reverse('reports:index')
    return HttpResponseSeeOther(index_uri)


def oauth(request):
    """Handle requests to use OAuth."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    vals = _get_oauth_values()
    auth_uri = _make_redirect(vals['redirect_uri'],
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

    response = requests.post(_OAUTH_URLS['token'], data={
        'code': request.GET['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': vals['redirect_uri'],
        'client_id': vals['client_id'],
        'client_secret': vals['client_secret'],
    })
    response.raise_for_status()
    data = response.json()

    # Save these in your database associated with the user
    access_token = data['access_token']
    refresh_token = data['refresh_token']
    expires_timestamp = datetime.datetime.now(pytz.utc) + \
                        datetime.timedelta(seconds=data['expires_in'])

    user = ReportsUser(user=request.user, access_token=access_token,
                refresh_token=refresh_token, expires=expires_timestamp)
    user.save()

    index_uri = urlresolvers.reverse('reports:index')
    return HttpResponseSeeOther(index_uri)
