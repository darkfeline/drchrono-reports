from itertools import chain
import datetime

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.db.models import Max, Min

import pytz

from .models import UserDoctor
from .models import UserTemplate
from .models import Field
from .models import Appointment


class ReportFilter(forms.Form):

    def _templates(self):
        return [('', '')] + [
            (x.template.id, x.template)
            for x in UserTemplate.objects.filter(user=self.user)]

    def _doctors(self):
        return [('', '')] + [
            (x.doctor.id, x.doctor)
            for x in UserDoctor.objects.filter(user=self.user)]

    def _fields(self):
        filter = Field.objects.filter(template=self.template)
        return [
            (x.id, x)
            for x in filter.exclude(name='')]

    def _years(self):
        doctors = UserDoctor.objects.filter(user=self.user)
        doctors = doctors.values_list('doctor', flat=True)
        filter = Appointment.objects.filter(
            doctor__in=doctors
        )
        end = filter.aggregate(Max('date'))['date__max']
        start = filter.aggregate(Min('date'))['date__min']
        return start.year, end.year

    def __init__(self, user, template=None, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.user = user
        self.template = template
        self.fields['doctor'] = forms.ChoiceField(
            label='Doctor', choices=self._doctors, required=False)
        self.fields['template'] = forms.ChoiceField(
            label='Template', choices=self._templates, required=False)
        if self.template:
            self.fields['fields'] = forms.MultipleChoiceField(
                label='Fields', choices=self._fields, required=False,
                widget=forms.CheckboxSelectMultiple)
        start, end = self._years()
        years = [x for x in xrange(start, end + 1)]
        self.fields['start_date'] = forms.DateField(
            label='Start date', required=False,
            widget=SelectDateWidget(years=years))
        self.fields['end_date'] = forms.DateField(
            label='End date', required=False,
            widget=SelectDateWidget(years=years))
