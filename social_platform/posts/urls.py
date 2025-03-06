from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    path('hashtag/<str:hashtag>/', views.hashtag_posts, name='hashtag_posts'),
    path('explore/', views.explore, name='explore'),
]