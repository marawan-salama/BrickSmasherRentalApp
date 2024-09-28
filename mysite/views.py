import re
from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models.functions import Lower
from .models import User, Movie, Checkout



class SimplePageView(View):
    template_name = ""

    def get(self, request):
        return render(request, self.template_name)

class HomePageView(SimplePageView):
    template_name = "home.html"

class AccountPageView(SimplePageView):
    template_name = "account.html"

class MoviePageView(SimplePageView):
    template_name = "movie.html"

class RentPageView(SimplePageView):
    template_name = "rent_return.html"


class UserManager(View):
    def get(self, request):
        email = request.GET.get("email")
        if not email:
            return JsonResponse({"error": "Email is required"}, status=400)
        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)
        return JsonResponse(self.serialize_user(user), safe=False)

    def post(self, request):
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        email = request.POST.get("email")

        if not first_name:
            return JsonResponse({"error": "First name is required"}, status=400)
        if not last_name:
            return JsonResponse({"error": "Last name is required"}, status=400)
        if not self.validate_email(email):
            return JsonResponse({"error": "Invalid email format"}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"error": "Email already exists"}, status=400)

        user = User.objects.create(first_name=first_name, last_name=last_name, email=email)
        return JsonResponse(self.serialize_user(user), safe=False)

    def serialize_user(self, user):
        return {
            "user_id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        }

    def validate_email(self, email):
        email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return re.match(email_pattern, email)


class MovieManager(View):
    def get(self, request):
        return self.list_movies()

    def post(self, request):
        action = request.POST.get("action")
        if action == "new":
            return self.create_movie(request)
        elif action in ["add", "remove"]:
            return self.modify_stock(request, action)
        return JsonResponse({"error": "Invalid action"}, status=400)

    def list_movies(self):
        queryset = Movie.objects.annotate(lowercase_title=Lower("title")).order_by("lowercase_title")
        movies = [self.format_movie_data(movie) for movie in queryset]
        return JsonResponse(movies, safe=False)

    def create_movie(self, request):
        title = request.POST.get("title", "").strip()
        if not title:
            return JsonResponse({"error": "Invalid title"}, status=400)
        if Movie.objects.filter(title__iexact=title).exists():
            return JsonResponse({"error": "Title already exists"}, status=400)

        movie = Movie.objects.create(title=title, stock=1)
        return JsonResponse(self.format_movie_data(movie), safe=False)

    def modify_stock(self, request, action):
        movie_id = request.POST.get("movie_id")
        movie = Movie.objects.filter(id=movie_id).first()
        if not movie:
            return JsonResponse({"error": "Invalid movie ID"}, status=400)

        if action == "add":
            movie.stock += 1
        elif action == "remove":
            if movie.stock <= 0:
                return JsonResponse({"error": "No copies in stock to remove"}, status=400)
            movie.stock -= 1
        movie.save()
        return JsonResponse(self.format_movie_data(movie), safe=False)

    def format_movie_data(self, movie):
        return {
            "movie_id": movie.id,
            "title": movie.title,
            "stock": movie.stock,
            "checked_out": movie.checked_out,
        }


class RentalManager(View):
    def get(self, request):
        return self.process_get_request(request)

    def post(self, request):
        return self.process_post_request(request)

    def process_get_request(self, request):
        user_id, movie_id = request.GET.get("user_id"), request.GET.get("movie_id")
        checkouts = self.get_filtered_checkouts(user_id, movie_id)

        if not user_id and not movie_id:
            return JsonResponse({"error": "User ID or Movie ID is required"}, status=400)

        result = self.serialize_checkouts(checkouts)
        return JsonResponse(result, safe=False)

    def get_filtered_checkouts(self, user_id, movie_id):
        checkouts = Checkout.objects.select_related("user", "movie").annotate(
            lowercase_title=Lower("movie__title")
        ).order_by("lowercase_title")

        if user_id:
            checkouts = checkouts.filter(user_id=user_id)
        if movie_id:
            checkouts = checkouts.filter(movie_id=movie_id)

        return checkouts

    def serialize_checkouts(self, checkouts):
        return [
            {
                "user_id": co.user.id,
                "email": co.user.email,
                "movie_id": co.movie.id,
                "title": co.movie.title,
                "checkout_date": co.date,
            }
            for co in checkouts
        ]

    def process_post_request(self, request):
        action = request.POST.get("action")
        user_id = request.POST.get("user_id")
        movie_id = request.POST.get("movie_id")

        if action == "rent":
            return self.process_rent(user_id, movie_id)
        elif action == "return":
            return self.process_return(user_id, movie_id)

    def process_rent(self, user_id, movie_id):
        user, movie = User.objects.filter(id=user_id).first(), Movie.objects.filter(id=movie_id).first()

        if not user or not movie:
            return JsonResponse({"error": "User or Movie not found"}, status=404)
        if Checkout.objects.filter(user=user, movie=movie).exists():
            return JsonResponse({"error": "Already checked out"}, status=400)
        if Checkout.objects.filter(user=user).count() >= 3:
            return JsonResponse({"error": "Checkout limit reached"}, status=400)

        self.create_checkout(user, movie)
        self.update_movie_stock(movie, increment=False)

        return JsonResponse(self.serialize_checkouts(Checkout.objects.filter(user_id=user_id)), safe=False)

    def process_return(self, user_id, movie_id):
        co = Checkout.objects.filter(user_id=user_id, movie_id=movie_id).first()
        if co:
            co.delete()
            movie = Movie.objects.get(id=movie_id)
            self.update_movie_stock(movie, increment=True)

        return JsonResponse(self.serialize_checkouts(Checkout.objects.filter(user_id=user_id)), safe=False)

    def create_checkout(self, user, movie):
        Checkout.objects.create(user=user, movie=movie)

    def update_movie_stock(self, movie, increment):
        if increment:
            movie.checked_out -= 1
            movie.stock += 1
        else:
            movie.checked_out += 1
            movie.stock -= 1
        movie.save()
