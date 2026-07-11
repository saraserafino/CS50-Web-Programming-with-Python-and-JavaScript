from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import User, Post, Follow, Like


def index(request):
    all_posts = Post.objects.all().order_by("id").reverse()##.prefetch_related('likes')

    # Pagination split by 10 posts at time
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    posts_in_page = paginator.get_page(page_number)

    # Add a is_liked field to each post
    for post in posts_in_page:
        post.is_liked = request.user in post.like.all() if request.user.is_authenticated else False

    return render(request, "network/index.html", {
        "allPosts": all_posts,
        "posts_in_page": posts_in_page
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def new_post(request):
    if request.method == "POST":
        content = request.POST['content']
        user = User.objects.get(pk=request.user.id)
        post = Post(content=content, user=user)
        post.save()
        return HttpResponseRedirect(reverse(index))

def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    all_posts = Post.objects.filter(user=user).order_by("id").reverse()##.prefetch_related('likes')

    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_followed=user)

    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(user=request.user, user_followed=user).exists()

    # Pagination split by 10 posts at time
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('page')
    posts_in_page = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "username": user.username,
        "allPosts": all_posts,
        "posts_in_page": posts_in_page,
        "following": following,
        "followers": followers,
        "is_following": is_following,
        "user_profile": user
    })

@login_required
def follow(request):
    user_to_follow = request.POST['followuser']
    data_user_to_follow = User.objects.get(username=user_to_follow)
    current_user = request.user
    f = Follow(user=current_user, user_followed=data_user_to_follow)
    f.save()

    return HttpResponseRedirect(reverse('profile', args=[data_user_to_follow.id]))

@login_required
def unfollow(request):
    user_to_unfollow = request.POST['unfollowuser']
    data_user_to_unfollow = User.objects.get(username=user_to_unfollow)
    current_user = request.user
    Follow.objects.filter(user=current_user, user_followed=data_user_to_unfollow).delete()

    return HttpResponseRedirect(reverse('profile', args=[data_user_to_unfollow.id]))

@login_required
def following(request):
    current_user = User.objects.get(pk=request.user.id)
    # Get all users the current user follows
    following_users = Follow.objects.filter(user=current_user).values_list('user_followed', flat=True)
    # Get posts from these users
    following_posts = Post.objects.filter(user__in=following_users).order_by("id").reverse()

    # Pagination
    paginator = Paginator(following_posts, 10)
    page_number = request.GET.get('page')
    posts_in_page = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts_in_page": posts_in_page,
    })

@login_required
def edit_post(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(pk=post_id)
        if request.user == post.user: # Only the owner of the post can edit
            post.content = request.POST.get("content", "")
            post.save()
            return JsonResponse({"success": True, "content": post.content})
        else:
            return JsonResponse({"success": False, "error": "Unauthorized"}, status=403)
    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)

@login_required
def toggle_like(request, post_id):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Unauthorized"}, status=401)

    post = Post.objects.get(pk=post_id)
    user = request.user

    # Check if the user already liked the post
    like, created = Like.objects.get_or_create(user=user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    # Return the updated like count
    like_count = post.like.count()
    return JsonResponse({"success": True, "liked": liked, "like_count": like_count})