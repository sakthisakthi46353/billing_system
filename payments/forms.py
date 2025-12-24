from django import forms
from .models import Payment
from invoices.models import Invoice


class PaymentForm(forms.ModelForm):

    class Meta:
        model = Payment
        fields = ['invoice', 'date', 'amount', 'method']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # ✅ IMPORTANT
        # Invoice dropdown should always have data
        self.fields['invoice'].queryset = Invoice.objects.all()
