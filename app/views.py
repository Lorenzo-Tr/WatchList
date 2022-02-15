from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render

from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from django.contrib import messages

from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView, FormView

from app.forms.login import LoginForm

from django.urls import reverse_lazy

from app.forms.register import RegisterForm


class IndexView(TemplateView):
    template_name = "block/index.html"

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result['title'] = "Home page"
        return result


class LoginFormView(FormView):
    template_name = 'block/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            # A backend authenticated the credentials
            login(self.request, user)
            messages.add_message(
                self.request, messages.INFO,
                f'Hello {user.username}'
            )
            return super().form_valid(form)
        form.add_error(None, "Email or Password invalid")
        return super().form_invalid(form)


class RegisterFormView(FormView):
    template_name = 'block/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('index')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        if user is not None:
            # A backend authenticated the credentials
            login(self.request, user)
            messages.add_message(
                self.request, messages.INFO,
                f'Hello {user.username}'
            )
            return super().form_valid(form)
        form.add_error(None, "Email or Password invalid")
        return super().form_invalid(form)

