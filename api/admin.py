from django.contrib import admin
from .models import Favorite, Like, Post, Profile, User

# Register your models here.

admin.site.register(Favorite)
admin.site.register(Like)
admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(User)
