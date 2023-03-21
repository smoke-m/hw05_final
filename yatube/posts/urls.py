from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    # Главная страница
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_posts_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path('posts/<int:post_id>/del/', views.post_del, name='post_del'),
    path('follow/', views.follow_index, name='follow_index'),
    path('authors/', views.authors_index, name='authors_index'),
    path('profile/<str:username>/follow/', views.profile_follow,
         name='profile_follow'),
    path('profile/<str:username>/unfollow/', views.profile_unfollow,
         name='profile_unfollow'),
    path('profile/<str:username>/followings/', views.author_followings,
         name='profile_followings'),
    path('profile/<str:username>/followers/', views.author_followers,
         name='profile_followers'),
    path('posts/<int:comment_id>/delcomment/',
         views.del_comment, name='del_comment'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment')
]
