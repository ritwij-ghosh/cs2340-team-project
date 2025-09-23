<<<<<<< HEAD
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

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

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Successfully logged out!')
    return redirect('home:index')
=======
from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'accounts/index.html')


def about(request):
    return render(request, 'accounts/about.html')
>>>>>>> c0c2653 (WIP)
