from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LogoutView
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect

from django.contrib import messages

from django.contrib.auth import authenticate, login
from django.utils.decorators import method_decorator
from django.views.generic import FormView, ListView, CreateView, UpdateView, DetailView

from app.exceptions import AlreadyExistsError
from app.forms.login import LoginForm

from django.urls import reverse_lazy

from app.forms.register import RegisterForm
from app.models import FriendshipRequest, Friendship, AnimeList, WatchList


class AnimeListView(ListView):
    template_name = "block/index.html"
    model = AnimeList

    def get_context_data(self, **kwargs):
        result = super().get_context_data(**kwargs)
        result['title'] = "Home page"
        if self.request.user.is_authenticated:
            result['watchlist'] = WatchList.objects.filter(user_id=self.request.user).values('anime_id')
        return result

    def post(self, request, *args, **kwargs):
        data = request.POST
        anime_id = AnimeList.objects.get(pk=request.POST['anime_id'])
        user_id = request.user
        WatchList.objects.create(user=user_id, anime=anime_id)
        return HttpResponseRedirect('/')


class AnimeAddView(CreateView):
    template_name = "block/animelist/add.html"
    model = AnimeList
    fields = ('title', 'summary', 'episode_duration', 'image', 'nb_episode', 'status_code')

    def get_success_url(self):
        return reverse_lazy('anime_list')


class AnimeUpdateView(UpdateView):
    template_name = "block/animelist/update.html"
    model = AnimeList
    fields = ('title', 'summary', 'episode_duration', 'image', 'nb_episode', 'status_code')

    def get_success_url(self):
        return reverse_lazy('anime_list')


class AnimeDetailView(LoginRequiredMixin, DetailView):
    template_name = "block/animelist/detail.html"
    model = AnimeList


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

    def get_success_url(self):
        url = self.request.GET.get('next', self.success_url)
        return url


class RegisterFormView(FormView):
    template_name = 'block/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        if user is not None:
            return super().form_valid(form)
        form.add_error(None, "Email or Password invalid")
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    next_page = 'index'
    template_name = 'block/index.html'


class AllUserView(ListView):
    template_name = "friendship/user_actions.html"
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.values()
        return context


class ProfileWatchListView(LoginRequiredMixin, ListView):
    login_url = 'login'
    template_name = "block/profile/watchlist.html"
    model = WatchList

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['path'] = self.request.path.split('/')
        return context

    def get_queryset(self):
        user_id = User.objects.filter(username=self.request.path.split('/')[2]).values('id')
        return WatchList.objects.filter(user_id__in=user_id).all


class ProfileView(LoginRequiredMixin, ListView):
    login_url = 'login'
    template_name = "block/profile/activity.html"
    model = WatchList

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        user_id = User.objects.filter(username=self.request.path.split('/')[2]).values('id')
        friends = Friendship.objects.filter(from_user__in=user_id).values('to_user')
        if friends is not None:
            context['friend_activity'] = WatchList.objects.filter(user_id__in=friends).all()
        context['user_activity'] = WatchList.objects.filter(user_id__in=user_id).all()
        return context


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
