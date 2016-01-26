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

    """Report filtering form."""

    def _templates(self):
        """Generate valid templates for selection."""
        return [('', '')] + [
            (x.template.id, x.template)
            for x in UserTemplate.objects.filter(user=self.user)]

    def _doctors(self):
        """Generate valid doctors for selection."""
        return [('', '')] + [
            (x.doctor.id, x.doctor)
            for x in UserDoctor.objects.filter(user=self.user)]

    def _fields(self):
        """Generate valid fields for selection."""
        filter = Field.objects.filter(template_id=self.template_id)
        return [
            (x.id, x)
            for x in filter.exclude(name='')]

    def _years(self):
        """Generate valid years for selection."""
        doctors = UserDoctor.objects.filter(user=self.user)
        doctors = doctors.values_list('doctor', flat=True)
        filter = Appointment.objects.filter(
            doctor__in=doctors
        )
        end = filter.aggregate(Max('date'))['date__max']
        start = filter.aggregate(Min('date'))['date__min']
        return start.year, end.year

    def __init__(self, user, template_id=None, *args, **kwargs):
        """Report filtering form.

        user is a ReportsUser object.  template_id is a template id as an int.

        """
        forms.Form.__init__(self, *args, **kwargs)
        self.user = user
        self.template_id = template_id
        self.fields['doctor'] = forms.ChoiceField(
            label='Doctor', choices=self._doctors, required=False)
        self.fields['template'] = forms.ChoiceField(
            label='Template', choices=self._templates, required=False)
        if self.template_id:
            self.fields['fields'] = forms.MultipleChoiceField(
                label='Fields', choices=self._fields, required=False)
        start, end = self._years()
        years = [x for x in xrange(start, end + 1)]
        self.fields['start_date'] = forms.DateField(
            label='Start date', required=False,
            widget=SelectDateWidget(years=years))
        self.fields['end_date'] = forms.DateField(
            label='End date', required=False,
            widget=SelectDateWidget(years=years))
