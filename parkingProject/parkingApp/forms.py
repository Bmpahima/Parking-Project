from django import forms
from django.core.validators import RegexValidator
from .models import User

class SignUpForm(forms.ModelForm):
    email = forms.EmailField(
        required=True,
        label='Email:'
    )
    password = forms.CharField(
        required=True,
        label='Password:',
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,30}$',
                message="Password must contain at least 8 characters, including 1 uppercase letter, 1 lowercase letter, and 1 number."
            )
        ]
    )
    phone_number = forms.CharField(
        label='Phone Number:',
        max_length=10,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^05\d{8}$',
                message="Phone number must start with '05' and contain 10 digits."
            )
        ]
    )
    license_plate_number = forms.CharField(
        label='License Number Plate:',
        max_length=8,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^\d{7,8}$',
                message="License plate number must contain 7-8 digits."
            )
        ]
    )

    class Meta:
        model = User
        #db_table = User ?
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password', 'license_plate']

    def clean_email(self,email):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

