# forms.py

from django import forms
from .models import Income, Outcome


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['quantity', 'location', 'delivery_order', 'comment']


class OutcomeForm(forms.ModelForm):
    class Meta:
        model = Outcome
        fields = ['qty', 'dest_location', 'comment']
