from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Wishlist


def index(request: HttpRequest) -> HttpResponse:
    listings = Listing.objects.order_by('-created')
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def listing(request: HttpRequest, id: int) -> HttpResponse:
    listing = Listing.objects.get(pk=id)
    user = request.user
    wishlisted = False

    # Check if wishlist already exists
    if user.is_authenticated and Wishlist.objects.filter(user=user, listing=listing).exists():
        wishlisted = True

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "wishlisted": wishlisted
    })


def create_listing(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return render(request, "auctions/create.html")
    else:
        try:
            title = request.POST['title']
            description = request.POST['description']
            price = float(request.POST['price'])
        except KeyError or TypeError:
            return render(request, "auctions/create.html", {
                'errorMessage': 'Fill form properly'
            })

        try:
            img_url = request.POST['url']
        except KeyError:
            img_url = None

        user = request.user

        listing = Listing(name=title, price=price, description=description, author = user, picture = img_url)
        listing.save()

        return render(request, "auctions/create.html", {
            'successMessage': 'Created listing successfully'
        })


def wishlist(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":

        listing_id = request.POST["id"]
        listing = Listing.objects.get(pk=listing_id)
        user = request.user

        # Check if wishlist already exists
        if Wishlist.objects.filter(user=user, listing=listing).exists():
            # Delete wishlist
            Wishlist.objects.filter(user=user, listing=listing).delete()
        else:
            _wishlist = Wishlist(user=user, listing=listing)
            _wishlist.save()

        return HttpResponseRedirect(reverse('index'))


def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        print('haha')
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
