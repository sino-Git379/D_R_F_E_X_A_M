from django.db.models import Avg, Count, Max, Min, Sum
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import Post, Profile, User
from .serializer import PostSerializer, ProfileSerializer, UserSerializer


@swagger_auto_schema(
    method="get",
    operation_summary="Получить список пользователей",
    operation_description="Возвращает пользователей с количеством публикаций, лайков и избранного.",
    responses={200: UserSerializer(many=True)},
)
@swagger_auto_schema(
    method="post",
    operation_summary="Создать пользователя",
    request_body=UserSerializer,
    responses={201: UserSerializer, 400: "Ошибка валидации"},
)
@api_view(["GET", "POST"])
def user_list_create(request):
    if request.method == "GET":
        users = User.objects.annotate(
            posts_count=Count("posts", distinct=True),
            likes_count=Count("likes", distinct=True),
            favorites_count=Count("favorites", distinct=True),
        )
        return Response(UserSerializer(users, many=True).data)

    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method="get",
    operation_summary="Получить пользователя",
    manual_parameters=[openapi.Parameter("pk", openapi.IN_PATH, description="ID пользователя", type=openapi.TYPE_INTEGER)],
    responses={200: UserSerializer, 404: "Пользователь не найден"},
)
@swagger_auto_schema(
    method="put",
    operation_summary="Полностью обновить пользователя",
    request_body=UserSerializer,
    responses={200: UserSerializer, 400: "Ошибка валидации", 404: "Пользователь не найден"},
)
@swagger_auto_schema(
    method="patch",
    operation_summary="Частично обновить пользователя",
    request_body=UserSerializer,
    responses={200: UserSerializer, 400: "Ошибка валидации", 404: "Пользователь не найден"},
)
@swagger_auto_schema(
    method="delete",
    operation_summary="Удалить пользователя",
    responses={204: "Пользователь удалён", 404: "Пользователь не найден"},
)
@api_view(["GET", "PUT", "PATCH", "DELETE"])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        return Response(UserSerializer(user).data)
    if request.method in ["PUT", "PATCH"]:
        serializer = UserSerializer(user, data=request.data, partial=request.method == "PATCH")
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(method="get", operation_summary="Самые активные пользователи", operation_description="Первые 10 пользователей по числу публикаций.", responses={200: openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={"id": openapi.Schema(type=openapi.TYPE_INTEGER), "username": openapi.Schema(type=openapi.TYPE_STRING), "posts_count": openapi.Schema(type=openapi.TYPE_INTEGER)}))})
@api_view(["GET"])
def most_active_users(request):
    users = User.objects.annotate(posts_count=Count("posts", distinct=True)).order_by("-posts_count")[:10]
    data = [{"id": u.id, "username": u.username, "posts_count": u.posts_count} for u in users]
    return Response(data)


@swagger_auto_schema(method="get", operation_summary="Статистика пользователей", responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={"total_users": openapi.Schema(type=openapi.TYPE_INTEGER), "average_age": openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT), "min_age": openapi.Schema(type=openapi.TYPE_INTEGER), "max_age": openapi.Schema(type=openapi.TYPE_INTEGER)})})
@api_view(["GET"])
def user_statistics(request):
    stats = User.objects.aggregate(total_users=Count("id"), average_age=Avg("age"), min_age=Min("age"), max_age=Max("age"))
    return Response(stats)


@swagger_auto_schema(method="get", operation_summary="Получить список профилей", responses={200: ProfileSerializer(many=True)})
@swagger_auto_schema(method="post", operation_summary="Создать профиль", request_body=ProfileSerializer, responses={201: ProfileSerializer, 400: "Ошибка валидации"})
@api_view(["GET", "POST"])
def profile_list_create(request):
    if request.method == "GET":
        profiles = Profile.objects.select_related("user").annotate(posts_count=Count("user__posts", distinct=True))
        return Response(ProfileSerializer(profiles, many=True).data)
    serializer = ProfileSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="get", operation_summary="Статистика профилей по городам", responses={200: openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT, properties={"city": openapi.Schema(type=openapi.TYPE_STRING), "users_count": openapi.Schema(type=openapi.TYPE_INTEGER)}))})
@api_view(["GET"])
def city_statistics(request):
    stats = Profile.objects.values("city").annotate(users_count=Count("id")).order_by("-users_count")
    return Response(list(stats))


@swagger_auto_schema(method="get", operation_summary="Получить список публикаций", responses={200: PostSerializer(many=True)})
@swagger_auto_schema(method="post", operation_summary="Создать публикацию", request_body=PostSerializer, responses={201: PostSerializer, 400: "Ошибка валидации"})
@api_view(["GET", "POST"])
def post_list_create(request):
    if request.method == "GET":
        posts = Post.objects.annotate(likes_count=Count("likes", distinct=True), favorites_count=Count("favorites", distinct=True))
        return Response(PostSerializer(posts, many=True).data)
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="get", operation_summary="Популярные публикации", operation_description="Публикации, набравшие не менее 10 лайков, отсортированные по числу лайков.", responses={200: PostSerializer(many=True)})
@api_view(["GET"])
def popular_posts(request):
    posts = Post.objects.annotate(likes_count=Count("likes", distinct=True)).filter(likes_count__gte=10).order_by("-likes_count")
    return Response(PostSerializer(posts, many=True).data)


@swagger_auto_schema(method="get", operation_summary="Статистика публикаций", responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={"total_posts": openapi.Schema(type=openapi.TYPE_INTEGER), "total_views": openapi.Schema(type=openapi.TYPE_INTEGER), "average_views": openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT), "max_views": openapi.Schema(type=openapi.TYPE_INTEGER), "min_views": openapi.Schema(type=openapi.TYPE_INTEGER), "total_likes": openapi.Schema(type=openapi.TYPE_INTEGER), "total_favorites": openapi.Schema(type=openapi.TYPE_INTEGER)})})
@api_view(["GET"])
def post_statistics(request):
    stats = Post.objects.aggregate(total_posts=Count("id"), total_views=Sum("views"), average_views=Avg("views"), max_views=Max("views"), min_views=Min("views"), total_likes=Count("likes"), total_favorites=Count("favorites"))
    return Response(stats)
