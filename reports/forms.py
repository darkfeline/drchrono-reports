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
        return [
            (x.template.id, x.template)
            for x in UserTemplate.objects.filter(user=self.user)]

    def _doctors(self):
        """Generate valid doctors for selection."""
        return [
            (x.doctor.id, x.doctor)
            for x in UserDoctor.objects.filter(user=self.user)]

    def _years(self):
        """Generate valid years for selection."""
        doctors = UserDoctor.objects.filter(user=self.user)
        doctors = doctors.values_list('doctor', flat=True)
        filter = Appointment.objects.filter(
            doctor__in=doctors
        )
        end = filter.aggregate(Max('date'))['date__max']
        start = filter.aggregate(Min('date'))['date__min']
        # No data
        if start is None:
            return None, None
        return start.year, end.year

    def __init__(self, user, *args, **kwargs):
        """Report filtering form.

        user is a ReportsUser object.  template_id is a template id as an int.

        """
        forms.Form.__init__(self, *args, **kwargs)
        self.user = user

        start, end = self._years()
        # Only add fields if there's data available.
        if start:
            years = [x for x in xrange(start, end + 1)]
            self.fields['start_date'] = forms.DateField(
                label='Start date', required=False,
                widget=SelectDateWidget(years=years))
            self.fields['end_date'] = forms.DateField(
                label='End date', required=False,
                widget=SelectDateWidget(years=years))
        # XXX This isn't very useful unless it can dynamically update the
        # template and fields inputs.
        #
        # If this is needed, easiest way is to create a separate report
        # endpoint.  I think.
        #
        # self.fields['archived'] = forms.BooleanField(
        #     label='Include archived', required=False)
        self.fields['doctors'] = forms.TypedMultipleChoiceField(
            label='Doctors', choices=self._doctors, coerce=int,
            required=False)
        self.fields['templates'] = forms.TypedMultipleChoiceField(
            label='Templates', choices=self._templates, coerce=int,
            required=False)
