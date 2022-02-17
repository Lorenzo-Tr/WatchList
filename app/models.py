from django.core.exceptions import ValidationError
from django.db import models

from django.contrib.auth.models import User

# Create your models here.
from django.db.models import Q
from django.utils import timezone

from app.exceptions import AlreadyExistsError, AlreadyFriendsError


class FriendshipRequest(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friendship_requests_sent",
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="friendship_requests_received",
    )
    datetime = models.DateTimeField(auto_now_add=True)

    class Status(models.TextChoices):
        REQUESTED = 'R'
        ACCEPTED = 'A'
        DECLINED = 'D'
        BLOCKED = 'B'

    status_code = models.TextField(max_length=1, choices=Status.choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['from_user', 'to_user'], name='Friendship Request')
        ]

    def __str__(self):
        return f"User #{self.to_user_id} Request user #{self.from_user_id} to be is friend"

    def accept(self):
        """ Accept this friendship request """
        Friendship.objects.create(from_user=self.from_user, to_user=self.to_user)

        Friendship.objects.create(from_user=self.to_user, to_user=self.from_user)

        self.delete()

        # Delete any reverse requests
        FriendshipRequest.objects.filter(
            from_user=self.to_user, to_user=self.from_user
        ).delete()

        return True

    def reject(self):
        """ reject this friendship request """
        self.rejected = timezone.now()
        self.save()
        return True


class FriendshipManager(models.Manager):
    def sent_requests(self, user):
        """ Return a list of friendship requests from user """
        qs = (
            FriendshipRequest.objects.select_related("from_user", "to_user")
                .filter(from_user=user)
                .all()
        )
        requests = list(qs)

        return requests

    def friends(self, user):
        """ Return a list of all friends """

        qs = (
            Friendship.objects.select_related("from_user", "to_user")
                .filter(to_user=user)
                .all()
        )
        friends = [u.from_user for u in qs]

        return friends

    def requests(self, user):
        """ Return a list of friendship requests """

        qs = (
            FriendshipRequest.objects.select_related("from_user", "to_user")
                .filter(to_user=user)
                .all()
        )
        requests = list(qs)

        return requests

    def add_friend(self, from_user, to_user, message=None):
        """ Create a friendship request """
        if from_user == to_user:
            raise ValidationError("Users cannot be friends with themselves")

        if self.are_friends(from_user, to_user):
            raise AlreadyFriendsError("Users are already friends")

        if FriendshipRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise AlreadyExistsError("You already requested friendship from this user.")

        if FriendshipRequest.objects.filter(from_user=to_user, to_user=from_user).exists():
            raise AlreadyExistsError("This user already requested friendship from you.")

        request, created = FriendshipRequest.objects.get_or_create(
            from_user=from_user, to_user=to_user
        )

        if created is False:
            raise AlreadyExistsError("Friendship already requested")

        if message:
            request.message = message
            request.save()

        return request

    def remove_friend(self, from_user, to_user):
        """ Destroy a friendship relationship """
        try:
            qs = Friendship.objects.filter(
                Q(to_user=to_user, from_user=from_user) | Q(to_user=from_user, from_user=to_user))
            distinct_qs = qs.distinct().all()

            if distinct_qs:
                qs.delete()
                return True
            else:
                return False
        except Friendship.DoesNotExist:
            return False

    def are_friends(self, user1, user2):
        """ Are these two users friends? """
        try:
            Friendship.objects.get(to_user=user1, from_user=user2)
            return True
        except Friendship.DoesNotExist:
            return False


class Friendship(models.Model):
    to_user = models.ForeignKey(User, models.CASCADE, related_name="friends")
    from_user = models.ForeignKey(
        User, models.CASCADE, related_name="_unused_friend_relation"
    )
    created = models.DateTimeField(default=timezone.now)

    objects = FriendshipManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['from_user', 'to_user'], name='Friend')
        ]

    def __str__(self):
        return f"User #{self.to_user_id} is friends with #{self.from_user_id}"

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.to_user == self.from_user:
            raise ValidationError("Users cannot be friends with themselves.")
        super().save(*args, **kwargs)


class AnimeList(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    episode_duration = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='covers/', blank=True, null=True)
    nb_episode = models.IntegerField(blank=True, null=True)

    class Status(models.TextChoices):
        FINISH = 'F', 'Finish'
        IN_PROGRESS = 'P', 'In Progress'

    status_code = models.TextField(max_length=1, choices=Status.choices)

    def __str__(self):
        return f"[{self.id}] {self.title}" or "? (no title) ?"


class WatchList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user",
    )
    anime = models.ForeignKey(
        AnimeList,
        on_delete=models.CASCADE,
        related_name="anime",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'anime_id'], name='whatchlist_add')
        ]

    progression = models.IntegerField(default=0)

    creation_date = models.DateTimeField(editable=False, blank=True)
    update_date = models.DateTimeField(blank=True)

    def save(self, *args, **kwargs):
        """ On save, update timestamps """
        if not self.id:
            self.creation_date = timezone.now()
        self.update_date = timezone.now()
        return super().save(*args, **kwargs)

