from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseRedirect
from django.core import urlresolvers

from .models import User
from .models import Template
from .models import Field
from .models import Values


class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303


def _make_flow():
    """Make flow object for OAuth."""
    return client.flow_from_clientsecrets(
        settings.DRCHRONO_BIRTHDAY_SECRETS,
        scope='patients user',
        redirect_uri='http://localhost:8000/birthday/auth_return/',
    )


def index(request):
    """Handle main page."""
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    try:
        user = User.objects.get(user=request.user)
    except User.DoesNotExist:
        index_uri = urlresolvers.reverse('reports:setup')
        return HttpResponseSeeOther(index_uri)
    last_updated_text = 'Last updated on {0:%x} at {0:%X}.'
    last_updated_text = last_updated_text.format(user.last_updated)
    context = {
        'name': user.name,
        'user': user.user,
        'last_updated': last_updated_text,
    }
    return render(request, 'reports/index.html', context)


def setup(request):
    """Handle initial user setup."""
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    context = {'user': request.user}
    return render(request, 'reports/setup.html', context)


def update(request):
    """Handle requests to update database using drchrono API."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    flow = _make_flow()
    auth_uri = flow.step1_get_authorize_url()
    FlowModel(user=request.user, flow=flow).save()
    return HttpResponseSeeOther(auth_uri)
