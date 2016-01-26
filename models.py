from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from oauth2client.django_orm import FlowField


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
    user = models.ForeignKey(ReportsUser)
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)

    def __unicode__(self):
        return '{}'.format(self.name)


class Template(models.Model):
    user = models.ForeignKey(ReportsUser)
    id = models.IntegerField(primary_key=True)
    doctor = models.ForeignKey(Doctor)
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return '{}'.format(self.name)


class Field(models.Model):
    user = models.ForeignKey(ReportsUser)
    id = models.IntegerField(primary_key=True)
    template = models.ForeignKey(Template)
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return '{}'.format(self.name)


class Value(models.Model):
    user = models.ForeignKey(ReportsUser)
    id = models.IntegerField(primary_key=True)
    field = models.ForeignKey(Field)
    value = models.TextField()

    def __unicode__(self):
        return '{}'.format(self.name)
