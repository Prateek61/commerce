from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    def __str__(self) -> str:
        return self.get_username()

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

class Listing(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(Category, related_name="listings", on_delete=models.CASCADE, null=True, blank=True)
    author = models.ForeignKey(User, related_name="listings", on_delete=models.CASCADE)
    picture = models.URLField(max_length=200, null=True, blank=True)

    def get_max_bid(self):
        try:
            # Get latest item
            return self.bids.latest('created').amount
        except Bid.DoesNotExist:
            return self.price

class Bid(models.Model):
    amount = models.FloatField()
    author = models.ForeignKey(User, related_name="bids", on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, related_name="bids", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, related_name="comments", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

class WatchList(models.Model):
    user = models.ForeignKey(User, related_name="wishlists", on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


