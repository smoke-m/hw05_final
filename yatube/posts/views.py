from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Post, Group, Follow, User
from .forms import PostForm, CommentForm


def paginator_def(queryset, page_number):
    return Paginator(queryset, settings.NUMB_POSTS).get_page(page_number)


def index(request):
    template = 'posts/index.html'
    posts = Post.objects.select_related('author', 'group')
    context = {
        'page_obj': paginator_def(posts, request.GET.get('page')),
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    context = {
        'group': group,
        'page_obj': paginator_def(posts, request.GET.get('page')),
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')
    following = request.user.is_authenticated and author.following.exists()
    context = {
        'author': author,
        'page_obj': paginator_def(posts, request.GET.get('page')),
        'following': following,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id)
    post_count = post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.select_related('post')
    context = {
        'post_count': post_count,
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id)
    if post.author == request.user:
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post,)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id)
        template = 'posts/edit_post.html'
        context = {
            'form': form,
        }
        return render(request, template, context)
    return redirect('posts:profile', request.user)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user)
    template = 'posts/create_post.html'
    context = {
        'form': form,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    authors = request.user.follower.values_list('author', flat=True)
    posts = Post.objects.select_related('author').filter(author_id__in=authors)
    template = 'posts/follow.html'
    context = {
        'page_obj': paginator_def(posts, request.GET.get('page')),
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:follow_index')
