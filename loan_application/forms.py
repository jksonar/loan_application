from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, LoanApplication, Document, LoanType

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'address')

class LoanEnquiryForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['loan_type', 'amount', 'tenure']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': 0}),
            'tenure': forms.NumberInput(attrs={'min': 1})
        }

    def clean(self):
        cleaned_data = super().clean()
        loan_type = cleaned_data.get('loan_type')
        amount = cleaned_data.get('amount')
        tenure = cleaned_data.get('tenure')

        if loan_type and amount and tenure:
            if amount > loan_type.max_amount:
                raise forms.ValidationError(f'Loan amount cannot exceed {loan_type.max_amount}')
            if tenure < loan_type.tenure_min or tenure > loan_type.tenure_max:
                raise forms.ValidationError(
                    f'Loan tenure must be between {loan_type.tenure_min} and {loan_type.tenure_max} months'
                )

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'file']
        widgets = {
            'file': forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'})
        }

class LoanApplicationUpdateForm(forms.ModelForm):
    class Meta:
        model = LoanApplication
        fields = ['status', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4})
        }

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3})
        }