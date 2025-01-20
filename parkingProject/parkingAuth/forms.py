# from django import forms
# from django.core.validators import RegexValidator
# from django.contrib.auth.models import User
# from parkingApp.util.license_api import get_car_detail
# from .models import UserProfile


# class UserRegistrationForm(forms.ModelForm):
#     # סיסמה עם וולידציה מותאמת
#     password = forms.CharField(
#         widget=forms.PasswordInput,
#         required=True,
#         validators=[
#             RegexValidator(
#                 regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$',
#                 message="Password must contain at least 8 characters, including 1 uppercase letter, 1 lowercase letter, and 1 number."
#             )
#         ]
#     )
#     # טלפון
#     phone_number = forms.CharField(
#         max_length=10,
#         required=True,
#         validators=[
#             RegexValidator(
#                 regex=r'^05\d{8}$',
#                 message="Phone number must start with '05' and contain 10 digits."
#             )
#         ]
#     )
#     # מספר רישוי
#     license_plate_number = forms.CharField(
#         max_length=8,
#         required=True,
#         validators=[
#             RegexValidator(
#                 regex=r'^\d{7,8}$',
#                 message="License plate number must contain 7-8 digits."
#             )
#         ]
#     )

#     class Meta:
#         model = User
#         # השדות מסודרים לפי הסדר שהוגדר
#         fields = ['first_name', 'last_name', 'email', 'password', 'phone_number', 'license_plate_number']

#     def save(self, commit=True):
#         user = super().save(commit=False)
#         # הצפנת סיסמה
#         user.set_password(self.cleaned_data['password'])
#         if commit:
#             user.save()

#             # שמירת פרופיל משתמש
#             license_plate_number = self.cleaned_data['license_plate_number']
#             car_details = get_car_detail(license_plate_number)

#             UserProfile.objects.create(
#                 # user=er,
#                 phone_number=self.cleaned_data['phone_number'],
#                 license_plate_number=license_plate_number,
#                 car_type=car_details.get('type'),
#                 car_year=car_details.get('year'),
#                 car_color=car_details.get('color'),
#                 car_model=car_details.get('model'),
#             )
#         return user
    

# class UserLoginForm(forms.Form):
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput)

#     def clean(self):
#         cleaned_data = super().clean()
#         email = cleaned_data.get('email')
#         password = cleaned_data.get('password')

#         if not email or not password:
#             raise forms.ValidationError("Both email and password are required!")

#         return cleaned_data
