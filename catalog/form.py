import datetime
from functools import partial
from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from catalog.models import BookInstance, Author


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        label="Renew Date",
        help_text="Enter a date between now and 4 weeks (default 3). Format : 08-11-2020")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # check if a date is in the past
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # check if a date is in the allowed range (+4 weeks from today)
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_("Invalid date - renewal more than 4 weeks ahead"))

        return data


class RenewBookModelForm(ModelForm):
    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _("New renewal date")}
        help_texts = {'due_back': _("Enter a date between new and 4 weeks (default 3).")}

    def clean_due_back(self):
        data = self.cleaned_data['due_back']

        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        return data


DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class AuthorCreateForm(ModelForm):
    date_of_birth = forms.DateField(widget=forms.DateInput(format='%m-%d-%Y',attrs={'class': 'datepicker'} ),
                                    input_formats=('%m-%d-%Y',))
    date_of_death = forms.DateField(widget=forms.DateInput(format='%m-%d-%Y'),
                                    input_formats=('%m-%d-%Y',))

    class Meta:
        model = Author
        fields = "__all__"
        help_texts = {
            "date_of_birth": "e.g 09-28-1990",
        }
        labels = {
            'date_of_birth': _("Date of birth (e.g 09-28-1990"),
            'first_name': _("First Name"),
            "last_name": _("Last Name"),
            "story": _("Story"), }
        # help_texts = {'due_back': _("Enter a date between new and 4 weeks (default 3).")}
