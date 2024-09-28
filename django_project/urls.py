"""
URL configuration for django_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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

# Import necessary Django utilities
from django.contrib import admin
from django.urls import path

# Import views from a single module
import mysite.views as views

# Define URL to view mapping in a list of tuples
url_configurations = [
    ("", views.HomePageView, "home"),
    ("account/", views.AccountPageView, "account"),
    ("movie/", views.MoviePageView, "movie"),
    ("rent/", views.RentPageView, "rent"),
    ("dbUser/", views.UserManager, "dbUser"),
    ("dbMovie/", views.MovieManager, "dbMovie"),
    ("dbRent/", views.RentalManager, "dbRent"),
]

# Use list comprehension to create urlpatterns
urlpatterns = [
    path(url, view.as_view(), name=name) for url, view, name in url_configurations
]
