from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile, SavedCandidateSearch
from .forms import ProfileForm, UserForm
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from communications.models import Message


def index(request):
    """Display all public profiles for browsing."""
    profiles = Profile.objects.filter(is_public=True)

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

    # US Cities and States for location dropdown
    location_choices = [
        ('', 'All Locations'),
        ('Remote', 'Remote'),
        ('Alabama', 'Alabama'),
        ('Alaska', 'Alaska'),
        ('Arizona', 'Arizona'),
        ('Arkansas', 'Arkansas'),
        ('California', 'California'),
        ('Colorado', 'Colorado'),
        ('Connecticut', 'Connecticut'),
        ('Delaware', 'Delaware'),
        ('Florida', 'Florida'),
        ('Georgia', 'Georgia'),
        ('Hawaii', 'Hawaii'),
        ('Idaho', 'Idaho'),
        ('Illinois', 'Illinois'),
        ('Indiana', 'Indiana'),
        ('Iowa', 'Iowa'),
        ('Kansas', 'Kansas'),
        ('Kentucky', 'Kentucky'),
        ('Louisiana', 'Louisiana'),
        ('Maine', 'Maine'),
        ('Maryland', 'Maryland'),
        ('Massachusetts', 'Massachusetts'),
        ('Michigan', 'Michigan'),
        ('Minnesota', 'Minnesota'),
        ('Mississippi', 'Mississippi'),
        ('Missouri', 'Missouri'),
        ('Montana', 'Montana'),
        ('Nebraska', 'Nebraska'),
        ('Nevada', 'Nevada'),
        ('New Hampshire', 'New Hampshire'),
        ('New Jersey', 'New Jersey'),
        ('New Mexico', 'New Mexico'),
        ('New York', 'New York'),
        ('North Carolina', 'North Carolina'),
        ('North Dakota', 'North Dakota'),
        ('Ohio', 'Ohio'),
        ('Oklahoma', 'Oklahoma'),
        ('Oregon', 'Oregon'),
        ('Pennsylvania', 'Pennsylvania'),
        ('Rhode Island', 'Rhode Island'),
        ('South Carolina', 'South Carolina'),
        ('South Dakota', 'South Dakota'),
        ('Tennessee', 'Tennessee'),
        ('Texas', 'Texas'),
        ('Utah', 'Utah'),
        ('Vermont', 'Vermont'),
        ('Virginia', 'Virginia'),
        ('Washington', 'Washington'),
        ('West Virginia', 'West Virginia'),
        ('Wisconsin', 'Wisconsin'),
        ('Wyoming', 'Wyoming'),
        ('Washington DC', 'Washington DC'),
        ('Atlanta, GA', 'Atlanta, GA'),
        ('Austin, TX', 'Austin, TX'),
        ('Boston, MA', 'Boston, MA'),
        ('Chicago, IL', 'Chicago, IL'),
        ('Dallas, TX', 'Dallas, TX'),
        ('Denver, CO', 'Denver, CO'),
        ('Detroit, MI', 'Detroit, MI'),
        ('Houston, TX', 'Houston, TX'),
        ('Los Angeles, CA', 'Los Angeles, CA'),
        ('Miami, FL', 'Miami, FL'),
        ('New York, NY', 'New York, NY'),
        ('Philadelphia, PA', 'Philadelphia, PA'),
        ('Phoenix, AZ', 'Phoenix, AZ'),
        ('San Antonio, TX', 'San Antonio, TX'),
        ('San Diego, CA', 'San Diego, CA'),
        ('San Francisco, CA', 'San Francisco, CA'),
        ('San Jose, CA', 'San Jose, CA'),
        ('Seattle, WA', 'Seattle, WA'),
        ('Tampa, FL', 'Tampa, FL'),
    ]

    context = {
        'profiles': profiles,
        'filters': {
            'skills': skills_query,
            'location': location_query,
            'projects': projects_query,
        },
        'location_choices': location_choices,
        'template_data': {'title': 'Profiles - HireBuzz'}
    }
    return render(request, 'profiles/index.html', context)


def _user_is_recruiter(user):
    if not user.is_authenticated:
        return False
    if hasattr(user, 'user_profile'):
        # Support either boolean helper methods or user_type field
        if hasattr(user.user_profile, 'is_recruiter') and callable(user.user_profile.is_recruiter):
            return bool(user.user_profile.is_recruiter())
        return getattr(user.user_profile, 'user_type', '') == 'recruiter'
    return False


@login_required
def save_search(request):
    """Save the current candidate search filters for a recruiter."""
    if not _user_is_recruiter(request.user):
        messages.error(request, 'Only recruiters can save candidate searches.')
        return redirect('profiles:index')

    skills = (request.GET.get('skills') or '').strip()
    location = (request.GET.get('location') or '').strip()
    projects = (request.GET.get('projects') or '').strip()

    # Disallow saving an empty search (no filters applied)
    if not any([skills, location, projects]):
        messages.warning(request, 'Add at least one filter before saving a search.')
        return redirect('profiles:index')

    # Avoid duplicates: if identical search exists, just acknowledge
    existing = SavedCandidateSearch.objects.filter(
        user=request.user, skills=skills, location=location, projects=projects
    ).first()
    if existing:
        messages.info(request, 'This search is already saved. You can access it from Saved Searches.')
        return redirect('profiles:saved_searches')

    SavedCandidateSearch.objects.create(
        user=request.user,
        skills=skills,
        location=location,
        projects=projects,
    )
    messages.success(request, 'Search saved successfully!')
    return redirect('profiles:saved_searches')


@login_required
def saved_searches(request):
    if not _user_is_recruiter(request.user):
        messages.error(request, 'Only recruiters can access saved candidate searches.')
        return redirect('profiles:index')
    searches = SavedCandidateSearch.objects.filter(user=request.user)
    context = {
        'searches': searches,
        'template_data': {'title': 'Saved Candidate Searches - HireBuzz'}
    }
    return render(request, 'profiles/saved_searches.html', context)


def _apply_profile_filters(queryset, skills, location, projects):
    if location:
        queryset = queryset.filter(location__icontains=location)
    if skills:
        raw_tokens = [token.strip() for token in skills.replace('\n', ' ').replace('\t', ' ').split(',')]
        tokens = []
        for chunk in raw_tokens:
            if not chunk:
                continue
            tokens.extend([t for t in chunk.split(' ') if t])
        for token in tokens:
            queryset = queryset.filter(skills__icontains=token)
    if projects:
        queryset = queryset.filter(
            Q(work_experience__icontains=projects)
            | Q(bio__icontains=projects)
            | Q(education__icontains=projects)
            | Q(linkedin_url__icontains=projects)
            | Q(github_url__icontains=projects)
            | Q(portfolio_url__icontains=projects)
            | Q(other_url__icontains=projects)
        )
    return queryset


@login_required
def run_saved_search(request, pk):
    """Run a saved search, send notification about new matches since last check, and show results."""
    if not _user_is_recruiter(request.user):
        messages.error(request, 'Only recruiters can run saved candidate searches.')
        return redirect('profiles:index')

    saved = get_object_or_404(SavedCandidateSearch, id=pk, user=request.user)
    profiles_qs = Profile.objects.filter(is_public=True)
    profiles_qs = _apply_profile_filters(profiles_qs, saved.skills, saved.location, saved.projects)

    # Determine new matches since last_checked_at
    if saved.last_checked_at:
        new_matches = profiles_qs.filter(updated_at__gt=saved.last_checked_at)
    else:
        new_matches = profiles_qs
    new_match_ids = list(new_matches.values_list('id', flat=True))

    # Send an in-platform message to the recruiter with a summary
    new_count = new_matches.count()
    if new_count > 0:
        subject = 'New candidate matches for your saved search'
        lines = [
            'You have new candidate matches on HireBuzz.',
            f"Filters: skills='{saved.skills or '-'}', location='{saved.location or '-'}', projects='{saved.projects or '-'}'",
            f'Total matches now: {profiles_qs.count()}',
            f'New since last check: {new_count}',
            '',
            'Top new matches:',
        ]
        for p in new_matches.select_related('user')[:5]:
            lines.append(f"- {p.user.get_full_name() or p.user.username} | {p.headline} | {p.location}")
        lines.append('\nVisit your saved searches to view all matches.')

        # Use a system sender to avoid duplicate sent/received for the recruiter
        system_user, _ = User.objects.get_or_create(
            username='system_notifications',
            defaults={'first_name': 'System', 'last_name': 'Notifications', 'email': ''}
        )
        Message.objects.create(
            sender=system_user,
            recipient=request.user,
            subject=subject,
            body='\n'.join(lines),
        )

    saved.last_checked_at = timezone.now()
    saved.last_notified_count = new_count
    saved.save(update_fields=['last_checked_at', 'last_notified_count'])

    context = {
        'saved_search': saved,
        'profiles': profiles_qs.select_related('user'),
        'new_count': new_count,
        'new_ids': new_match_ids,
        'template_data': {'title': 'Saved Search Results - HireBuzz'}
    }
    return render(request, 'profiles/saved_searches.html', context)


@login_required
def delete_saved_search(request, pk):
    if not _user_is_recruiter(request.user):
        messages.error(request, 'Only recruiters can manage saved candidate searches.')
        return redirect('profiles:index')
    saved = get_object_or_404(SavedCandidateSearch, id=pk, user=request.user)
    saved.delete()
    messages.success(request, 'Saved search deleted.')
    return redirect('profiles:saved_searches')


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

    is_owner = request.user.is_authenticated and request.user == user
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
