from django import forms
from django.core.validators import RegexValidator
from .models import User
from django.core.validators import MinLengthValidator,MaxLengthValidator



class UserRegistrationForm(forms.ModelForm):
    
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$',
                message="Password must contain at least 8 characters, including 1 uppercase letter, 1 lowercase letter, and 1 number."
            )
        ]
    )
    phone_number = forms.CharField(
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
        max_length=8,
        required=True,
        validators=[
            RegexValidator(
            regex=r'^\d{7,8}$',
            message="license plate number contain 7-8 digits."
            )]
        )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password', 'license_plate']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email
    

class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)