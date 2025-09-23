<<<<<<< HEAD
from django.shortcuts import render

def index(request):
    context = {
        'template_data': {'title': 'Home - HireBuzz'}
    }
    return render(request, 'home/index.html', context)
=======
from django.shortcuts import render

def index(request):
    return render(request, 'home/index.html')
>>>>>>> c0c2653 (WIP)
