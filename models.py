from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from oauth2client.django_orm import FlowField


class FlowModel(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    flow = FlowField()

    def __unicode__(self):
        return '{}'.format(self.user)


class User(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    name = models.CharField(max_length=256)
    last_updated = models.DateTimeField()

    def __unicode__(self):
        return '{}'.format(self.user)


class Template(models.Model):
    id = models.IntegerField(primary_key=True)
    doctor = models.IntegerField()
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return '{}'.format(self.name)


class Field(models.Model):
    id = models.IntegerField(primary_key=True)
    template = models.ForeignKey(Template)
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return '{}'.format(self.name)


class Values(models.Model):
    id = models.IntegerField(primary_key=True)
    field = models.ForeignKey(Field)
    value = models.TextField()

    def __unicode__(self):
        return '{}'.format(self.name)
