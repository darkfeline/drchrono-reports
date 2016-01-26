from __future__ import unicode_literals
from __future__ import division

import datetime

from django.shortcuts import render
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core import urlresolvers

import pytz
import requests

from .models import ReportsUser
from .models import Doctor
from .models import Template
from .models import Field
from .models import Value
from .models import UserDoctor
from .models import UserTemplate
from .models import Appointment

from .forms import ReportFilter

from . import oauthlib
from . import errors


class HttpResponseSeeOther(HttpResponseRedirect):
    status_code = 303


class HttpResponseTemporaryRedirect(HttpResponseRedirect):
    status_code = 307


def _get_oauth_values():
    return {
        'client_id': 'GcFaMT8rcTQW1VWIMPWiKwt5T1APHP2u0mmQleyP',
        'client_secret': 'X368VErNf1dVG2LSrI5zCbATokpvTzg8V2gULhylt8PZrpE7su9hsmOiIiHQgQsG8MeHzK1t1i60fkVKRBv83wP6tgA39ALpPyAk1TV2LwLYcWYvcPBg1iyog4D7ta7f',
        'scope': 'patients user calendar',
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
    if user.access_token:
        connected = 'Connected.'
    else:
        connected = 'Not connected.'
    context = {
        'user': user.user,
        'connected': connected,
        'last_updated': last_updated_text,
    }
    return render(request, 'reports/index.html', context)


def _generate_data(user, doctor=None, template=None, fields=None,
                   start_date=None, end_date=None):
    """Generate report data lazily.

    Takes the following filter arguments:

    doctor filters by doctor id given as int.  template filters by template id
    as int.  fields filters by a list of field ids as int.

    fields must be used with template.

    """

    # Handle filters.  Do any necessary type conversions, set up queries, and
    # check permissions.
    if doctor:
        if not UserDoctor.objects.filter(user=user, doctor=doctor).exists():
            raise errors.PermissionError()
        app_q = Appointment.objects.filter(doctor=doctor)
    else:
        app_q = Appointment.objects.all()

    field_q = Field.objects.exclude(name='')
    if template:
        if not UserTemplate.objects.filter(
                user=user, template=template).exists():
            raise errors.PermissionError()
        template_q = UserTemplate.objects.filter(template=template)
        field_q = field_q.filter(template=template)
        if fields:
            field_q = field_q.filter(id__in=fields)
    else:
        template_q = UserTemplate.objects.filter(user=user)

    if template and fields:
        field_q = field_q.filter(template=template)

    # XXX Optimize this with SQL join?
    # XXX Super inefficient!
    # Generate rows of data.
    for usertemplate in template_q:
        template = usertemplate.template
        fields = Field.objects.filter(template=template)
        total = 0
        for appointment in app_q:
            template_used = Value.objects.filter(appointment=appointment)
            template_used = template_used.filter(field__in=fields).exists()
            if template_used:
                total += 1
        for field in field_q:
            count = 0
            for appointment in Appointment.objects.all():
                if Value.objects.filter(field=field,
                                        appointment=appointment).exists():
                    count += 1
            yield (template.name, field.name, '{}/{}'.format(count, total),
                   '{:.1%}'.format(count / total) if total else 'N/A')


def view_report(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    user = ReportsUser.objects.get(user=request.user)

    # Get arguments and convert types.
    filters = {
        'doctor': request.GET.get('doctor'),
        'template': request.GET.get('template'),
    }
    # Convert non-empty strings to int.
    # Convert empty strings to None.
    for key, value in filters.items():
        filters[key] = int(value) if value else None
    filters['fields'] = [int(x) for x in request.GET.getlist('fields')]

    template = filters['template']
    template = Template.objects.get(id=template) if template else None
    data = _generate_data(user, **filters)
    context = {
        'data': data,
        'form': ReportFilter(user, template, request.GET),
    }
    return render(request, 'reports/view_report.html', context)


def update(request):
    """Update data from drchrono."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    user = ReportsUser.objects.get(user=request.user)
    now = datetime.datetime.now(pytz.utc)

    # OAuth not set up.
    if not user.expires:
        index_uri = urlresolvers.reverse('reports:oauth')
        return HttpResponseSeeOther(index_uri)

    # Refresh if needed.
    if user.expires - datetime.timedelta(minutes=10) < now:
        user.refresh()

    headers = user.auth_header()

    # XXX Skip updating existing?

    # Update doctors.
    url = oauthlib.url('/api/doctors')
    while url:
        data = requests.get(url, headers=headers).json()
        for entry in data['results']:
            Doctor.objects.update_or_create(
                id=entry['id'],
                first_name=entry['first_name'],
                last_name=entry['last_name'])
            UserDoctor.objects.get_or_create(
                user=user, doctor=entry['id'])
        url = data['next']

    # Update templates.
    url = oauthlib.url('/api/clinical_note_templates')
    while url:
        data = requests.get(url, headers=headers).json()
        for entry in data['results']:
            Template.objects.update_or_create(
                id=entry['id'],
                doctor=entry['doctor'],
                name=entry['name'])
            UserTemplate.objects.get_or_create(
                user=user, template=entry['id'])
        url = data['next']

    # Update fields.
    url = oauthlib.url('/api/clinical_note_field_types')
    while url:
        data = requests.get(url, headers=headers).json()
        for entry in data['results']:
            Field.objects.update_or_create(
                id=entry['id'],
                template=entry['clinical_note_template'],
                name=entry['name'])
        url = data['next']

    # Update values.
    url = oauthlib.url('/api/clinical_note_field_values')
    while url:
        data = requests.get(url, headers=headers).json()
        for entry in data['results']:
            # Make appointment.
            app_id = entry['appointment']
            url = oauthlib.url('/api/appointments/{}'.format(app_id))
            data2 = requests.get(url, headers=headers).json()
            app, created = Appointment.objects.update_or_create(
                id=app_id, doctor=data2['doctor'])

            # Make value.
            Value.objects.update_or_create(
                id=entry['id'],
                field=_entry['clinical_note_field'],
                appointment=app)
        url = data['next']

    user.last_updated = now
    user.save()

    index_uri = urlresolvers.reverse('reports:index')
    return HttpResponseSeeOther(index_uri)


def oauth(request):
    """Handle requests to use OAuth."""
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
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

    user = ReportsUser.objects.get(user=request.user)
    user.access_token = access_token
    user.refresh_token = refresh_token
    user.expires = expires_timestamp
    user.save()

    index_uri = urlresolvers.reverse('reports:index')
    return HttpResponseSeeOther(index_uri)
