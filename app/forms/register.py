from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from django import forms


class RegisterForm(UserCreationForm):
    password1 = forms.CharField(
        min_length=2,
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["email", "username", "password1", "password2"]

