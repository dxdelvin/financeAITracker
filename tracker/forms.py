from django import forms
from .models import Transaction


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'category', 'transaction_type', 'comment', 'date_created']
        widgets = {
            'date_created': forms.DateInput(attrs={'type': 'date'})
        }

    # Custom validations or widgets can be added here if needed
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if float(amount) <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount
