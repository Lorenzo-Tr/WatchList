from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect

from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from django.contrib import messages

from django.contrib.auth import authenticate, login
from django.views.generic import TemplateView, FormView

from app.exceptions import AlreadyExistsError
from app.forms.login import LoginForm

from django.urls import reverse_lazy

from app.forms.register import RegisterForm
from app.models import FriendshipRequest, Friendship


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


def all_users(request, template_name="friendship/user_actions.html"):
    users = User.objects.all()

    return render(
        request, template_name, {get_friendship_context_object_list_name(): users}
    )


def get_friendship_context_object_name():
    return getattr(settings, "FRIENDSHIP_CONTEXT_OBJECT_NAME", "user")


def get_friendship_context_object_list_name():
    return getattr(settings, "FRIENDSHIP_CONTEXT_OBJECT_LIST_NAME", "users")


def view_friends(request, username, template_name="friendship/friend/user_list.html"):
    """ View the friends of a user """
    user = get_object_or_404(User, username=username)
    friends = Friendship.objects.friends(user)
    return render(
        request,
        template_name,
        {
            get_friendship_context_object_name(): user,
            "friendship_context_object_name": get_friendship_context_object_name(),
            "friends": friends,
        },
    )


@login_required
def friendship_add_friend(
    request, to_username, template_name="friendship/friend/add.html"
):
    """ Create a FriendshipRequest """
    ctx = {"to_username": to_username}

    if request.method == "POST":
        to_user = User.objects.get(username=to_username)
        from_user = request.user
        try:
            Friendship.objects.add_friend(from_user, to_user)
        except AlreadyExistsError as e:
            ctx["errors"] = ["%s" % e]
        else:
            return redirect("friendship_request_list")

    return render(request, template_name, ctx)


@login_required
def friendship_accept(request, friendship_request_id):
    """ Accept a friendship request """
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.friendship_requests_received, id=friendship_request_id
        )
        f_request.accept()
        return redirect("friendship_view_friends", username=request.user.username)

    return redirect(
        "friendship_requests_detail", friendship_request_id=friendship_request_id
    )


@login_required
def friendship_reject(request, friendship_request_id):
    """ Reject a friendship request """
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.friendship_requests_received, id=friendship_request_id
        )
        f_request.reject()
        return redirect("friendship_request_list")

    return redirect(
        "friendship_requests_detail", friendship_request_id=friendship_request_id
    )


@login_required
def friendship_cancel(request, friendship_request_id):
    """ Cancel a previously created friendship_request_id """
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.friendship_requests_sent, id=friendship_request_id
        )
        f_request.cancel()
        return redirect("friendship_request_list")

    return redirect(
        "friendship_requests_detail", friendship_request_id=friendship_request_id
    )


@login_required
def friendship_request_list(
    request, template_name="friendship/friend/requests_list.html"
):
    """ View unread and read friendship requests """
    friendship_requests = Friendship.objects.requests(request.user)
    # This shows all friendship requests in the database
    # friendship_requests = FriendshipRequest.objects.filter(rejected__isnull=True)

    return render(request, template_name, {"requests": friendship_requests})


@login_required
def friendship_request_list_rejected(
    request, template_name="friendship/friend/requests_list.html"
):
    """ View rejected friendship requests """
    # friendship_requests = Friend.objects.rejected_requests(request.user)
    friendship_requests = FriendshipRequest.objects.filter(rejected__isnull=False)

    return render(request, template_name, {"requests": friendship_requests})


@login_required
def friendship_requests_detail(
    request, friendship_request_id, template_name="friendship/friend/request.html"
):
    """ View a particular friendship request """
    f_request = get_object_or_404(FriendshipRequest, id=friendship_request_id)

    return render(request, template_name, {"friendship_request": f_request})