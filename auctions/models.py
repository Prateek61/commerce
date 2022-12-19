from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50)
    picture = models.ImageField(upload_to='images/')

class Bid(models.Model):
    amount = models.FloatField()
    user = models.ForeignKey(User, related_name="bids", on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, related_name="bids", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, related_name="comments", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)



