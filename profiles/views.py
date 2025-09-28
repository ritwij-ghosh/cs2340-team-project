from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from .forms import ProfileForm, UserForm
from django.db.models import Q
from accounts.models import UserProfile


def index(request):
    """Display all public profiles for browsing - only job seekers can be viewed by recruiters."""
    # Only show job seeker profiles to recruiters, and only if user is authenticated
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to browse profiles.')
        return redirect('accounts:login')
    
    # Check if current user is a recruiter
    try:
        user_profile = request.user.user_profile
        if not user_profile.is_recruiter():
            messages.warning(request, 'Only recruiters can browse candidate profiles.')
            return redirect('jobs:index')
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile setup first.')
        return redirect('profiles:create')
    
    # Only show job seeker profiles
    profiles = Profile.objects.filter(
        is_public=True,
        user__user_profile__user_type='job_seeker'
    )

    # Filtering for recruiter search
    skills_query = (request.GET.get('skills') or '').strip()
    location_query = (request.GET.get('location') or '').strip()
    projects_query = (request.GET.get('projects') or '').strip()

    if location_query:
        profiles = profiles.filter(location__icontains=location_query)

    if skills_query:
        # Split by comma and/or whitespace, match profiles whose skills contain all tokens
        raw_tokens = [token.strip() for token in skills_query.replace('\n', ' ').replace('\t', ' ').split(',')]
        tokens = []
        for chunk in raw_tokens:
            if not chunk:
                continue
            tokens.extend([t for t in chunk.split(' ') if t])
        for token in tokens:
            profiles = profiles.filter(skills__icontains=token)

    if projects_query:
        # Search across work experience and common profile text/link fields
        profiles = profiles.filter(
            Q(work_experience__icontains=projects_query)
            | Q(bio__icontains=projects_query)
            | Q(education__icontains=projects_query)
            | Q(linkedin_url__icontains=projects_query)
            | Q(github_url__icontains=projects_query)
            | Q(portfolio_url__icontains=projects_query)
            | Q(other_url__icontains=projects_query)
        )

    context = {
        'profiles': profiles,
        'filters': {
            'skills': skills_query,
            'location': location_query,
            'projects': projects_query,
        },
        'template_data': {'title': 'Candidate Profiles - HireBuzz'}
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
    """View a specific user's public profile - with privacy controls."""
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in to view profiles.')
        return redirect('accounts:login')
    
    user = get_object_or_404(User, id=user_id)
    try:
        profile = user.profile
        user_profile = user.user_profile
    except (Profile.DoesNotExist, UserProfile.DoesNotExist):
        messages.error(request, 'This user does not have a public profile.')
        return redirect('profiles:index')

    is_owner = request.user == user
    
    # Privacy controls: Only recruiters can view job seeker profiles
    try:
        current_user_profile = request.user.user_profile
        if not is_owner:
            if current_user_profile.is_recruiter() and user_profile.is_job_seeker():
                # Recruiter viewing job seeker - allowed
                pass
            elif current_user_profile.is_job_seeker() and user_profile.is_recruiter():
                # Job seeker trying to view recruiter - not allowed
                messages.warning(request, 'Job seekers cannot view recruiter profiles.')
                return redirect('jobs:index')
            elif current_user_profile.is_job_seeker() and user_profile.is_job_seeker():
                # Job seeker trying to view another job seeker - not allowed
                messages.warning(request, 'Job seekers cannot view other job seeker profiles.')
                return redirect('jobs:index')
            else:
                messages.warning(request, 'You do not have permission to view this profile.')
                return redirect('profiles:index')
    except UserProfile.DoesNotExist:
        messages.warning(request, 'Please complete your profile setup first.')
        return redirect('profiles:create')
    
    if not profile.is_public and not is_owner and not request.user.is_staff:
        messages.warning(request, 'This profile is currently set to private.')
        return redirect('profiles:index')

    context = {
        'profile': profile,
        'profile_user': user,
        'is_owner': is_owner,
        'template_data': {'title': f'{user.get_full_name() or user.username} - Profile - HireBuzz'}
    }
    return render(request, 'profiles/view_profile.html', context)
