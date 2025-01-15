from django import forms
from django.core.validators import RegexValidator
from .models import User
from django.core.validators import MinLengthValidator,MaxLengthValidator
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login


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
            raise forms.ValidationError("This email is already in use, Please try another email.")
        return email
    

class UserLoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if not username or not password:
            raise forms.ValidationError("Both username and password are required!!")

        user = authenticate(username=username, password=password)
        if user is None:
            raise forms.ValidationError("Invalid username or password, please try again.")
        
        login(self.request, user)

        return cleaned_data
    
