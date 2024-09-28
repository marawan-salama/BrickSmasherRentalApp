from django.db import models

class BaseModel(models.Model):
    """
    An abstract base class model that provides self-updating
    'created' and 'modified' fields.
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Person(BaseModel):
    """
    Abstract base class for person-related details.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    class Meta:
        abstract = True

class User(Person):
    """
    User model to store user specific data.
    """
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['last_name', 'first_name']

class Movie(BaseModel):
    """
    Movie model to store movie inventory details.
    """
    title = models.CharField(max_length=200, unique=True)
    stock = models.PositiveIntegerField(default=0)
    checked_out = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Movie"
        verbose_name_plural = "Movies"
        ordering = ['title']

class Checkout(BaseModel):
    """
    Checkout model that records each movie checkout by a user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkouts')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='checkouts')
    date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Checkout"
        verbose_name_plural = "Checkouts"
        ordering = ['-date']
