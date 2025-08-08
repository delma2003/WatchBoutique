from django import forms

class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(max_length=15, label="Phone Number")

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6, label="Enter OTP")
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Address  # Import Address model

class CustomUserCreationForm(UserCreationForm):
    address = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter your address'})
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'address']
