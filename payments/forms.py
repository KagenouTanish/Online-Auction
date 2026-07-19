from django import forms
from .models import Payment


class PaymentForm(forms.Form):
    payment_method = forms.ChoiceField(
        choices=Payment.PAYMENT_METHODS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
