from django import template

from app.models import Friendship

register = template.Library()


@register.simple_tag(takes_context=True)
def get_by_name(context, name):
    """Tag to lookup a variable in the current context."""
    return context[name]


@register.inclusion_tag("friendship/templatetags/friends.html")
def friends(user):
    """
    Simple tag to grab all friends
    """
    return {"friends": Friendship.objects.friends(user)}


@register.inclusion_tag("friendship/templatetags/friend_requests.html")
def friend_requests(user):
    """
    Inclusion tag to display friend requests
    """
    return {"friend_requests": Friendship.objects.requests(user)}


@register.inclusion_tag("friendship/templatetags/friend_request_count.html")
def friend_request_count(user):
    """
    Inclusion tag to display the count of unread friend requests
    """
    return {"friend_request_count": Friendship.objects.unread_request_count(user)}


@register.inclusion_tag("friendship/templatetags/friend_count.html")
def friend_count(user):
    """
    Inclusion tag to display the total count of friends for the given user
    """
    return {"friend_count": len(Friendship.objects.friends(user))}


@register.inclusion_tag("friendship/templatetags/friend_rejected_count.html")
def friend_rejected_count(user):
    """
    Inclusion tag to display the count of rejected friend requests
    """
    return {"friend_rejected_count": len(Friendship.objects.rejected_requests(user))}
