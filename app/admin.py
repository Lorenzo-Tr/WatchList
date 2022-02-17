from django.contrib import admin

from app.models import Friendship, FriendshipRequest, AnimeList


class FriendAdmin(admin.ModelAdmin):
    model = Friendship
    raw_id_fields = ("to_user", "from_user")


class FriendshipRequestAdmin(admin.ModelAdmin):
    model = FriendshipRequest
    raw_id_fields = ("from_user", "to_user")


admin.site.register(Friendship, FriendAdmin)
admin.site.register(FriendshipRequest, FriendshipRequestAdmin)
admin.site.register(AnimeList)

