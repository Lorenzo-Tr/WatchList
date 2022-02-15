"""Python URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app.views import IndexView, LoginFormView, RegisterFormView, friendship_requests_detail, \
    friendship_request_list_rejected, friendship_request_list, friendship_cancel, friendship_reject, friendship_accept, \
    friendship_add_friend, view_friends, all_users

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name="index"),
    path('login/', LoginFormView.as_view(), name="login"),
    path('register/', RegisterFormView.as_view(), name="register"),
    path('users/', view=all_users, name="friendship_view_users"),
    path('friends/<slug:username>/', view=view_friends,
         name="friendship_view_friends",
         ),
    path('friend/add/<slug:to_username>/', view=friendship_add_friend,
         name="friendship_add_friend",
         ),
    path('friend/accept/<int:friendship_request_id>/', view=friendship_accept,
         name="friendship_accept",
         ),
    path('friend/reject/<int:friendship_request_id>/', view=friendship_reject,
         name="friendship_reject",
         ),
    path('friend/cancel/<int:friendship_request_id>/', view=friendship_cancel,
         name="friendship_cancel",
         ),
    path('friend/requests/', view=friendship_request_list,
         name="friendship_request_list",
         ),
    path('friend/requests/rejected/', view=friendship_request_list_rejected,
         name="friendship_requests_rejected",
         ),
    path('friend/request/<int:friendship_request_id>/', view=friendship_requests_detail,
         name="friendship_requests_detail",
         ),
]
