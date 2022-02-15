from django.forms import Form
from django import forms


class LoginForm(Form):
    username = forms.CharField(max_length=200)
    password = forms.CharField(
        max_length=200,
        widget=forms.PasswordInput
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        # if not email.endswith("etu.univ-amu.fr"):
        #     self.add_error('email', 'Vous devez faire partie de l\'Univ AMU')
        return username

