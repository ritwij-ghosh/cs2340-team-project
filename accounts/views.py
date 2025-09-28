from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from .forms import JobSeekerRegistrationForm, RecruiterRegistrationForm
from .models import UserProfile

def index(request):
    context = {
        'template_data': {'title': 'Account - HireBuzz'}
    }
    return render(request, 'accounts/index.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Successfully logged in!')
            return redirect('profiles:index')
        else:
            messages.error(request, 'Invalid username or password.')
    
    context = {
        'template_data': {'title': 'Login - HireBuzz'}
    }
    return render(request, 'accounts/login.html', context)


def register_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'You already have an account.')
        return redirect('profiles:my_profile')

    context = {
        'template_data': {'title': 'Create Account - HireBuzz'}
    }
    return render(request, 'accounts/register.html', context)


def register_job_seeker(request):
    """Register a new job seeker."""
    if request.user.is_authenticated:
        messages.info(request, 'You already have an account.')
        return redirect('profiles:my_profile')

    if request.method == 'POST':
        form = JobSeekerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                user_type='job_seeker'
            )
            login(request, user)
            messages.success(request, 'Welcome to HireBuzz! Let\'s build your professional profile next.')
            return redirect('profiles:create')
    else:
        form = JobSeekerRegistrationForm()

    context = {
        'form': form,
        'template_data': {'title': 'Sign Up as Job Seeker - HireBuzz'}
    }
    return render(request, 'accounts/register_job_seeker.html', context)


def register_recruiter(request):
    """Register a new recruiter."""
    if request.user.is_authenticated:
        messages.info(request, 'You already have an account.')
        return redirect('profiles:my_profile')

    if request.method == 'POST':
        form = RecruiterRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile with company info
            UserProfile.objects.create(
                user=user,
                user_type='recruiter',
                company=form.cleaned_data['company']
            )
            login(request, user)
            messages.success(request, 'Welcome to HireBuzz! You can now start posting jobs.')
            return redirect('jobs:post_job')
    else:
        form = RecruiterRegistrationForm()

    context = {
        'form': form,
        'template_data': {'title': 'Sign Up as Recruiter - HireBuzz'}
    }
    return render(request, 'accounts/register_recruiter.html', context)

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('home:index')
