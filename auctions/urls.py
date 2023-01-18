from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("listing/<int:id>", views.listing_view, name="listing"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create"),
    path("watchlist", views.watchlist, name='watchlist'),
    path("categoies", views.all_categories, name="categories"),
    path("category/<str:category>", views.category, name="category"),
    path("comment", views.comment, name="comment"),
    path("bid", views.bid, name="bid"),
    path("close", views.close_listing, name="close"),
]
