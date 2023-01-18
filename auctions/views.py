from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, WatchList, Category, Comment, Bid


def index(request: HttpRequest) -> HttpResponse:
    # FILTER OUT INACTIVE LISTINGS
    listings = Listing.objects.filter(active=True).order_by('-created')
    return render(request, "auctions/index.html", {
        "listings": listings,
        "title": "Active Listings"
    })


def listing_view(request: HttpRequest, id: int, status: int = 200, errorMessage: str = None) -> HttpResponse:
    listing = Listing.objects.get(pk=id)
    user = request.user
    watchlisted = False

    # Check if WatchList already exists
    if user.is_authenticated and WatchList.objects.filter(user=user, listing=listing).exists():
        watchlisted = True

    # Get all comments
    comments = Comment.objects.filter(listing=listing).order_by('-created')

    # Get the most recent bid
    try:
        last_bid = Bid.objects.filter(listing=listing).latest('created').amount
    except Bid.DoesNotExist:
        last_bid = None
    
    # Get the user's bid
    users_bid = None
    if user.is_authenticated:
        try:
            users_bid = Bid.objects.filter(listing=listing, author=user).latest('created').amount
        except Bid.DoesNotExist:
            users_bid = None

    # Check if user is the author of the listing
    is_author = False
    if user.is_authenticated and listing.author == user:
        isAuthor = True

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watchlisted": watchlisted,
        "comments": comments,
        "max_bid": last_bid,
        "users_bid": users_bid,
        "errorMessage": errorMessage,
        "isAuthor": isAuthor
    }, status=status)

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
    listings = Listing.objects.filter(category=category, active=True).order_by('-created')

    return render(request, "auctions/index.html", {
        "listings": listings,
        "title": f"Active Listings({category.name})"
    })

def all_categories(request: HttpRequest) -> HttpResponse:
    categories = Category.objects.all()

    return render(request, "auctions/categories.html", {
        "categories": categories
    })

@login_required
def comment(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        try:
            listing_id = int(request.POST['id'])
            content = request.POST['content']
        except KeyError or TypeError:
            return listing_view(request, listing_id, 400, 'Fill form properly')

        listing = Listing.objects.get(pk=listing_id)
        user = request.user

        comment = Comment(content=content, author=user, listing=listing)
        comment.save()

        return HttpResponseRedirect(reverse('listing', args=(listing_id,)))

@login_required
def bid(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        try:
            bid = float(request.POST['bid'])
            listing_id = int(request.POST['id'])
        except KeyError or TypeError:
            return listing(request, listing_id, 400, 'Fill form properly')

        listing = Listing.objects.get(pk=listing_id)
        user = request.user

        # Get the most recent bid
        try:
            last_bid = Bid.objects.filter(listing=listing).latest('created')
        except Bid.DoesNotExist:
            last_bid = None

        # Check if bid is higher than the last bid
        if last_bid is not None and bid <= last_bid.amount:
            return listing_view(request, listing_id, 400, 'Bid must be higher than the last bid')

        # Check if bid is higher than the starting price
        if bid <= listing.price:
            return listing_view(request, listing_id, 400, 'Bid must be higher than the starting price')

        # Create new bid
        new_bid = Bid(amount=bid, author=user, listing=listing)
        new_bid.save()

        return HttpResponseRedirect(reverse('listing', args=(listing_id,)))

@login_required
def close_listing(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        listing_id = request.POST['id']
        listing = Listing.objects.get(pk=listing_id)

        # Check if user is the author of the listing
        if listing.author != request.user:
            return listing_view(request, listing_id, 400, 'You are not the author of this listing')

        # Check if listing is already closed
        if not listing.active:
            return listing_view(request, listing_id, 400, 'Listing is already closed')

        # Close listing
        listing.active = False
        listing.save()

        return HttpResponseRedirect(reverse('listing', args=(listing_id,)))

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
            }, status=400)
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
