from . import views
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="API documentation",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('api/users/', views.user_list_create, name='user-list-create'),
    path('api/users/<int:pk>/', views.user_detail, name='user-detail'),
    path('api/users/most-active/', views.most_active_users, name='most-active-users'),
    path('api/users/statistics/', views.user_statistics, name='user-statistics'),
    path('api/profiles/', views.profile_list_create, name='profile-list-create'),
    path('api/profiles/city-statistics/', views.city_statistics, name='city-statistics'),
    path('api/posts/', views.post_list_create, name='post-list-create'),
    path('api/posts/popular/', views.popular_posts, name='popular-posts'),
    path('api/posts/statistics/', views.post_statistics, name='post-statistics'),

        # Swagger UI
    re_path(
        r'^swagger/$',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),

    # ReDoc
    re_path(
        r'^redoc/$',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),


]