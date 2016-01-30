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

from django.db import models
from django.contrib.auth.models import User

from . import errors


class ReportsUser(models.Model):
    user = models.OneToOneField(User, primary_key=True)

    access_token = models.CharField(max_length=256)
    refresh_token = models.CharField(max_length=256)
    expires = models.DateTimeField(null=True)

    last_updated = models.DateTimeField(null=True)

    def __unicode__(self):
        return '{}'.format(self.user)

    def refresh(self):
        """Refresh access token."""
        if not user.refresh_token:
            raise errors.NoTokenError
        response = requests.post(_OAUTH_URLS['token'], data={
            'refresh_token': user.refresh_token,
            'grant_type': 'refresh_token',
            'client_id': vals['client_id'],
            'client_secret': vals['client_secret'],
        })

        response.raise_for_status()
        data = response.json()

        user.access_token = data['access_token']
        user.refresh_token = data['refresh_token']
        user.expires = datetime.datetime.now(pytz.utc) + \
                    datetime.timedelta(seconds=data['expires_in'])
        user.save()

    def auth_header(self):
        """Return HTTP header with OAuth token."""
        return {
            'Authorization': 'Bearer {}'.format(self.access_token),
        }


class Doctor(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)

    def __unicode__(self):
        return '{}'.format(' '.join((self.first_name, self.last_name.upper())))


class UserDoctor(models.Model):
    user = models.ForeignKey(ReportsUser)
    doctor = models.ForeignKey(Doctor)
    class Meta:
        unique_together = ('user', 'doctor')

    def __unicode__(self):
        return '{}'.format(self.id)


class Template(models.Model):
    id = models.IntegerField(primary_key=True)
    doctor = models.ForeignKey(Doctor)
    name = models.CharField(max_length=256)
    archived = models.BooleanField()

    def __unicode__(self):
        return '{}'.format(self.name)


class UserTemplate(models.Model):
    user = models.ForeignKey(ReportsUser)
    template = models.ForeignKey(Template)
    class Meta:
        unique_together = ('user', 'template')

    def __unicode__(self):
        return '{}'.format(self.id)


class Field(models.Model):
    id = models.IntegerField(primary_key=True)
    template = models.ForeignKey(Template)
    name = models.CharField(max_length=256)
    archived = models.BooleanField()

    def __unicode__(self):
        return '{}'.format(self.name)


class Appointment(models.Model):
    id = models.IntegerField(primary_key=True)
    doctor = models.ForeignKey(Doctor)
    date = models.DateField()

    def __unicode__(self):
        return '{}'.format(self.id)


class Value(models.Model):
    id = models.IntegerField(primary_key=True)
    field = models.ForeignKey(Field)
    appointment = models.ForeignKey(Appointment)

    def __unicode__(self):
        return '{}'.format(self.name)
