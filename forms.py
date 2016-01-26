from django import forms

from .models import UserDoctor
from .models import Doctor


class ReportFilter(forms.Form):

    def _doctors(self):
        return ((x.doctor.id, x.doctor)
                for x in UserDoctor.objects.filter(user=self.user))

    def __init__(self, user, *args, **kwargs):
        forms.Form.__init__(self, *args, **kwargs)
        self.user = user
        self.fields['doctor'] = forms.ChoiceField(
            label='Doctor', choices=self._doctors)
