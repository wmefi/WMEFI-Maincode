from django import forms
from .models import Doctor, Survey, Question, Answer

class DoctorLoginForm(forms.Form):
    mobile = forms.CharField(max_length=15, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter your mobile number'
    }))

class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter OTP'
    }))

class DoctorProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial value for profession field
        if 'profession' in self.fields:
            self.fields['profession'].initial = 'Dr.'
            self.fields['profession'].widget.attrs.update({
                'class': 'form-control',
                'readonly': 'readonly',
                'style': 'background-color: #e9ecef; cursor: not-allowed;'
            })

    class Meta:
        model = Doctor
        fields = [
            'mobile', 'first_name', 'last_name', 'email', 'gender', 'address',
            'state', 'city', 'pincode', 'profession', 'specialty', 'degree',
            'diploma', 'pg_degree', 'diplomate', 'superspeciality',
            'mci_registration', 'pan', 'pan_copy', 'cancelled_cheque',
            'prescription_name', 'prescription_file', 'clinic_name', 'qualification',
            'gst_number', 'has_gst', 'bank_account_name', 'bank_name',
            'account_no', 'branch', 'ifsc'
        ]
        widgets = {
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email ID'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pincode'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Specialty'}),
            'degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Degree'}),
            'diploma': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Diploma'}),
            'pg_degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PG Degree'}),
            'diplomate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Diplomate'}),
            'superspeciality': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Superspeciality'}),
            'mci_registration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MCI Registration No'}),
            'pan': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PAN No.'}),
            'clinic_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Clinic Name'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Qualification'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'GST Number'}),
            'bank_account_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name as per Bank Account'}),
            'bank_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank Name'}),
            'account_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Account No'}),
            'branch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Branch'}),
            'ifsc': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IFSC'}),
            'prescription_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prescription Name'}),
        }

class SurveyUploadForm(forms.Form):
    file = forms.FileField(label='Upload Survey File (JSON or Excel)')