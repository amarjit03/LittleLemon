from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Comment, Like, Hashtag
from .forms import PostForm, CommentForm
from django.db.models import Q
import re
from users.models import FriendRequest, User

@login_required
def home(request):
    # Get IDs of friends (users with accepted friend requests)
    friend_ids = FriendRequest.objects.filter(
        (Q(from_user=request.user) | Q(to_user=request.user)) & Q(status='accepted')
    ).values_list('from_user', 'to_user')
    
    # Flatten and remove duplicates
    friend_ids_flat = set()
    for from_id, to_id in friend_ids:
        friend_ids_flat.add(from_id)
        friend_ids_flat.add(to_id)
    friend_ids_flat.discard(request.user.id)
    
    # Get posts from friends and self
    timeline_posts = Post.objects.filter(
        Q(user__in=friend_ids_flat) | Q(user=request.user)
    ).order_by('-created_at')
    
    # Handle new post creation
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            
            # Extract and save hashtags
            hashtag_pattern = r'#(\w+)'
            hashtags = re.findall(hashtag_pattern, post.content)
            for tag in hashtags:
                hashtag, created = Hashtag.objects.get_or_create(name=tag.lower())
                hashtag.posts.add(post)
                
            return redirect('home')
    else:
        form = PostForm()
        
    context = {
        'posts': timeline_posts,
        'form': form,
    }
    return render(request, 'posts/home.html', context)
    
@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()
            return redirect('post_detail', post_id=post.id)
    else:
        comment_form = CommentForm()
        
    # Check if user has liked the post
    user_has_liked = Like.objects.filter(post=post, user=request.user).exists()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'user_has_liked': user_has_liked,
    }
    return render(request, 'posts/post_detail.html', context)
    
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(post=post, user=request.user)
    
    if not created:
        # User already liked this post, unlike it
        like.delete()
        
    return redirect('post_detail', post_id=post.id)
    
@login_required
def hashtag_posts(request, hashtag):
    hashtag_obj = get_object_or_404(Hashtag, name=hashtag.lower())
    posts = hashtag_obj.posts.all()
    
    context = {
        'hashtag': hashtag_obj,
        'posts': posts,
    }
    return render(request, 'posts/hashtag_posts.html', context)
    
@login_required
def explore(request):
    # Show posts from non-friends, ordered by popularity (likes count)
    posts = Post.objects.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
    return render(request, 'posts/explore.html', {'posts': posts})