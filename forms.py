from itertools import chain

from django import forms

from .models import UserDoctor
from .models import UserTemplate


class ReportFilter(forms.Form):

    def _templates(self):
        return [('', '')] + [
            (x.template.id, x.template)
            for x in UserTemplate.objects.filter(user=self.user)]

    def _doctors(self):
        return [('', '')] + [
            (x.doctor.id, x.doctor)
            for x in UserDoctor.objects.filter(user=self.user)]

    def __init__(self, user, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.user = user
        self.fields['doctor'] = forms.ChoiceField(
            label='Doctor', choices=self._doctors, required=False)
        self.fields['template'] = forms.ChoiceField(
            label='Template', choices=self._templates, required=False)
