from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ProfileUpdateForm
from .models import User, FriendRequest

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})
    
@login_required
def profile(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
        is_self = user == request.user
    else:
        user = request.user
        is_self = True
        
    context = {
        'profile_user': user,
        'is_self': is_self,
    }
    return render(request, 'users/profile.html', context)
    
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})
    
@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    return redirect('profile', username=to_user.username)
    
@login_required
def friend_requests(request):
    friend_requests = FriendRequest.objects.filter(to_user=request.user, status='pending')
    return render(request, 'users/friend_requests.html', {'friend_requests': friend_requests})
    
@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
    friend_request.status = 'accepted'
    friend_request.save()
    return redirect('friend_requests')