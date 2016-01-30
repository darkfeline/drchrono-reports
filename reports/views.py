from __future__ import unicode_literals
from __future__ import division

import datetime
from functools import partial

from django.shortcuts import render
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.core import urlresolvers
from django import forms

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


def index(request):
    """Handle index page.

    Create internal user if it doesn't exist.

    Expose UI functions for reporting, oauth, updating.

    """
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
        'form': ReportFilter(user),
        'form_target': urlresolvers.reverse('reports:view_report'),
    }
    return render(request, 'reports/index.html', context)


def _generate_data(user, doctors=None, templates=None, fields=None,
                   start_date=None, end_date=None,
                   archived=None):
    """Generate report data lazily.

    Takes the following filter arguments:

    doctors, templates, and fields are lists of int ids.

    start_date and end_date are date objects.

    archived is a bool.

    """

    # Build valid IDs lists.
    template_ids = UserTemplate.objects.filter(user=user)
    template_ids = template_ids.values_list('template_id', flat=True)
    doctor_ids = UserDoctor.objects.filter(user=user)
    doctor_ids = doctor_ids.values_list('doctor_id', flat=True)

    # Build filters and check permissions.
    app_q = Appointment.objects.all()
    templ_q = Template.objects.filter(id__in=template_ids)
    field_q = Field.objects.exclude(name='')
    if not archived:
        templ_q = templ_q.filter(archived=False)
        field_q = field_q.filter(archived=False)
    if doctors:
        if not all(doctor in doctor_ids for doctor in doctors):
            raise errors.PermissionError()
        app_q = app_q.filter(doctor_id__in=doctors)
    if templates:
        if not all(template in template_ids for template in templates):
            raise errors.PermissionError()
        templ_q = Template.objects.filter(id__in=templates)
        field_q = field_q.filter(template_id__in=templates)
    if fields:
        field_q = field_q.filter(id__in=fields)
    if start_date:
        app_q = app_q.filter(date__gte=start_date)
    if end_date:
        app_q = app_q.filter(date__lte=end_date)

    # XXX Optimize this with SQL join?
    # XXX Super inefficient!
    # Generate rows of data.
    for template in templ_q:
        fields = Field.objects.filter(template=template)
        total = 0
        for appointment in app_q:
            template_used = Value.objects.filter(appointment=appointment)
            template_used = template_used.filter(field__in=fields).exists()
            if template_used:
                total += 1
        for field in field_q.filter(template_id=template):
            count = 0
            for appointment in app_q:
                if Value.objects.filter(field=field,
                                        appointment=appointment).exists():
                    count += 1
            yield (template.name, field.name, '{}/{}'.format(count, total),
                   '{:.1%}'.format(count / total) if total else 'N/A')


def _test_field(template_id, field_id):
    """Test field validity.

    Test if field is a valid field of given template.

    """
    return Field.objects.filter(id=field_id,
                                template_id=template_id).exists()


def _clean_fields(templates, request):
    """Clean field parameters.

    Return a cleaned list of fields.

    """

    fields = list()
    for template_id in templates:
        param_id = 'template_{}'.format(template_id)
        field_ids = request.GET.getlist(param_id)
        field_ids = [int(id) for id in field_ids]
        field_ids = filter(partial(_test_field, template_id), field_ids)
        fields.extend(field_ids)
    return fields


def pre_report_archived(request, archived=False):
    """Portal to reporting with archived.

    """
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    user = ReportsUser.objects.get(user=request.user)

    # Create form for cleaning data.
    form = ReportFilter(user, request.GET)
    form.is_valid()

    context = {
        'form': ReportFilter(user, request.GET),
        'form_target': urlresolvers.reverse('reports:view_report_archived'),
    }
    return render(request, 'reports/pre_report_archived.html', context)


def view_report(request, archived=False):
    """View report.

    Parse GET parameters for filtering and generate data using filtering.

    """
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    user = ReportsUser.objects.get(user=request.user)

    # Create form for cleaning data.
    form = ReportFilter(user, request.GET)
    form.is_valid()

    filters = dict()
    filters['doctors'] = form.cleaned_data.get('doctors')
    filters['templates'] = form.cleaned_data.get('templates')
    filters['start_date'] = form.cleaned_data.get('start_date')
    filters['end_date'] = form.cleaned_data.get('end_date')
    filters['archived'] = archived

    filters['fields'] = _clean_fields(filters['templates'], request)

    data = _generate_data(user, **filters)
    context = {
        'data': data,
        'form': ReportFilter(user, request.GET),
        'form_target': (urlresolvers.reverse('reports:view_report_archived')
                        if archived else
                        urlresolvers.reverse('reports:view_report')),
    }
    return render(request, 'reports/view_report.html', context)


def dynamic_fields(request):
    """Render dynamic_fields.js

    The reason we have this here instead of as a static file is that the path
    of AJAX calls cannot be hard-coded and need to be rendered here.

    """
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    return render(request, 'reports/dynamic_fields.js',
                  content_type='application/javascript')


def template_fields(request):
    """template_fields AJAX handler.

    Return fields of given template.

    """
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    user = ReportsUser.objects.get(user=request.user)

    template_id = int(request.GET['id'])
    template_name = Template.objects.get(id=template_id).name
    data = Field.objects.filter(template_id=template_id).exclude(name='')
    data = [(field.id, field.name) for field in data]
    data = {
        'id': template_id,
        'name': template_name,
        'fields': data,
    }
    return JsonResponse(data)


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
                user=user, doctor_id=entry['id'])
        url = data['next']

    # Update templates.
    url = oauthlib.url('/api/clinical_note_templates')
    while url:
        data = requests.get(url, headers=headers).json()
        for entry in data['results']:
            Template.objects.update_or_create(
                id=entry['id'],
                doctor_id=entry['doctor'],
                name=entry['name'],
                archived=entry['archived'])
            UserTemplate.objects.get_or_create(
                user=user, template_id=entry['id'])
        url = data['next']

    # Update fields.
    url = oauthlib.url('/api/clinical_note_field_types')
    while url:
        data = requests.get(url, headers=headers).json()
        for entry in data['results']:
            Field.objects.update_or_create(
                id=entry['id'],
                template_id=entry['clinical_note_template'],
                name=entry['name'],
                archived=entry['archived'])
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
            date = datetime.datetime.strptime(
                data2['scheduled_time'], "%Y-%m-%dT%H:%M:%S")
            app, created = Appointment.objects.update_or_create(
                id=app_id, doctor_id=data2['doctor'],
                date=date)

            # Make value.
            Value.objects.update_or_create(
                id=entry['id'],
                field_id=entry['clinical_note_field'],
                appointment=app)
        url = data['next']

    user.last_updated = now
    user.save()

    index_uri = urlresolvers.reverse('reports:index')
    return HttpResponseSeeOther(index_uri)


def oauth(request):
    """Initiate OAuth."""
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])
    vals = oauthlib.get_secrets()
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

    vals = oauthlib.get_secrets()

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
