from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

from .forms import RegistrationForm

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

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome to HireBuzz! Let’s build your profile next.')
            return redirect('profiles:create')
    else:
        form = RegistrationForm()

    context = {
        'form': form,
        'template_data': {'title': 'Create Account - HireBuzz'}
    }
    return render(request, 'accounts/register.html', context)

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('home:index')
