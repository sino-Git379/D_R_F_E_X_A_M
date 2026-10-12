from datetime import timedelta
from django.db.models import Avg, Count, Max, Min, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Favorite, Like, Post, Profile, User
from .serializer import FavoriteSerializer, LikeSerializer, PostSerializer, ProfileSerializer, UserSerializer


@api_view(["GET", "POST"])
def user_list_create(request):
    if request.method == "GET":
        users = User.objects.annotate(
            posts_count=Count("posts", distinct=True),
            likes_count=Count("likes", distinct=True),
            favorites_count=Count("favorites", distinct=True),
        )
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method in ["PUT", "PATCH"]:
        partial = request.method == "PATCH"
        serializer = UserSerializer(user, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def most_active_users(request):
    users = (
        User.objects.annotate(posts_count=Count("posts", distinct=True))
        .order_by("-posts_count")[:10]
    )
    data = [
        {"id": u.id, "username": u.username, "posts_count": u.posts_count}
        for u in users
    ]
    return Response(data)


@api_view(["GET"])
def user_statistics(request):
    stats = User.objects.aggregate(
        total_users=Count("id"),
        average_age=Avg("age"),
        min_age=Min("age"),
        max_age=Max("age"),
    )
    return Response(stats)


@api_view(["GET", "POST"])
def profile_list_create(request):
    if request.method == "GET":
        profiles = Profile.objects.select_related("user").annotate(
            posts_count=Count("user__posts", distinct=True)
        )
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = ProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def city_statistics(request):
    stats = (
        Profile.objects.values("city")
        .annotate(users_count=Count("id"))
        .order_by("-users_count")
    )
    return Response(list(stats))


@api_view(["GET", "POST"])
def post_list_create(request):
    if request.method == "GET":
        posts = Post.objects.annotate(
            likes_count=Count("likes", distinct=True),
            favorites_count=Count("favorites", distinct=True),
        )
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def popular_posts(request):
    posts = (
        Post.objects.annotate(likes_count=Count("likes", distinct=True))
        .filter(likes_count__gte=10)
        .order_by("-likes_count")
    )
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def post_statistics(request):
    stats = Post.objects.aggregate(
        total_posts=Count("id"),
        total_views=Sum("views"),
        average_views=Avg("views"),
        max_views=Max("views"),
        min_views=Min("views"),
        total_likes=Count("likes"),
        total_favorites=Count("favorites"),
    )
    return Response(stats)