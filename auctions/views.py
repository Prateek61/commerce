from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, WatchList, Category


def index(request: HttpRequest) -> HttpResponse:
    listings = Listing.objects.order_by('-created')
    return render(request, "auctions/index.html", {
        "listings": listings,
        "title": "Active Listings"
    })


def listing(request: HttpRequest, id: int) -> HttpResponse:
    listing = Listing.objects.get(pk=id)
    user = request.user
    watchlisted = False

    # Check if WatchList already exists
    if user.is_authenticated and WatchList.objects.filter(user=user, listing=listing).exists():
        watchlisted = True

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlisted": watchlisted
    })

@login_required
def create_listing(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        categories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": categories
        })
    else:
        try:
            title = request.POST['title']
            description = request.POST['description']
            price = float(request.POST['price'])
        except KeyError or TypeError:
            return render(request, "auctions/create.html", {
                'errorMessage': 'Fill form properly'
            })

        category_id = int(request.POST['category'])
        try:
            category = Category.objects.get(pk=category_id)
        except Category.DoesNotExist:
            category = None

        try:
            img_url = request.POST['url']
        except KeyError:
            img_url = None

        user = request.user

        listing = Listing(name=title, price=price, description=description, author = user, category=category, picture = img_url)
        listing.save()

        return render(request, "auctions/create.html", {
            'successMessage': 'Created listing successfully'
        })

@login_required
def watchlist(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":

        listing_id = request.POST["id"]
        listing = Listing.objects.get(pk=listing_id)
        user = request.user

        # Check if WatchList already exists
        if WatchList.objects.filter(user=user, listing=listing).exists():
            # Delete WatchList
            WatchList.objects.filter(user=user, listing=listing).delete()
        else:
            _watchlist = WatchList(user=user, listing=listing)
            _watchlist.save()

        return HttpResponseRedirect(reverse('listing', args=(listing_id,)))

    else:
        user = request.user
        watchlist = WatchList.objects.filter(user=user).order_by('-created')
        listings = [watchlist_item.listing for watchlist_item in watchlist]

        return render(request, "auctions/index.html", {
            "listings": listings,
            "title": "Watchlist"
        })

def category(request: HttpRequest, category: str) -> HttpResponse:
    category = Category.objects.get(name=category)
    listings = Listing.objects.filter(category=category).order_by('-created')

    return render(request, "auctions/index.html", {
        "listings": listings,
        "title": f"Active Listings({category.name})"
    })

def all_categories(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.all()

    return render(request, "auctions/categories.html", {
        "categories": categories
    })

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

@login_required
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
