from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from .forms import ProfileForm, UserForm


def index(request):
    """Display all public profiles for browsing."""
    profiles = Profile.objects.all()
    context = {
        'profiles': profiles,
        'template_data': {'title': 'Profiles - HireBuzz'}
    }
    return render(request, 'profiles/index.html', context)


@login_required
def my_profile(request):
    """Display the current user's profile."""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('profiles:create')
    
    context = {
        'profile': profile,
        'template_data': {'title': 'My Profile - HireBuzz'}
    }
    return render(request, 'profiles/my_profile.html', context)


@login_required
def create_profile(request):
    """Create a new profile for the current user."""
    if hasattr(request.user, 'profile'):
        messages.info(request, 'You already have a profile. You can edit it instead.')
        return redirect('profiles:edit')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Your profile has been created successfully!')
            return redirect('profiles:my_profile')
    else:
        form = ProfileForm()
    
    context = {
        'form': form,
        'template_data': {'title': 'Create Profile - HireBuzz'}
    }
    return render(request, 'profiles/create_profile.html', context)


@login_required
def edit_profile(request):
    """Edit the current user's profile."""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('profiles:create')
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profiles:my_profile')
    else:
        form = ProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile,
        'template_data': {'title': 'Edit Profile - HireBuzz'}
    }
    return render(request, 'profiles/edit_profile.html', context)


@login_required
def edit_user_info(request):
    """Edit the current user's basic information."""
    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account information has been updated successfully!')
            return redirect('profiles:my_profile')
    else:
        form = UserForm(instance=request.user)
    
    context = {
        'form': form,
        'template_data': {'title': 'Edit Account Info - HireBuzz'}
    }
    return render(request, 'profiles/edit_user_info.html', context)


def view_profile(request, user_id):
    """View a specific user's public profile."""
    user = get_object_or_404(User, id=user_id)
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        messages.error(request, 'This user does not have a public profile.')
        return redirect('profiles:index')
    
    context = {
        'profile': profile,
        'profile_user': user,
        'template_data': {'title': f'{user.get_full_name() or user.username} - Profile - HireBuzz'}
    }
    return render(request, 'profiles/view_profile.html', context)
