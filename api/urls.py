from django.urls import path
from . import views

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
]