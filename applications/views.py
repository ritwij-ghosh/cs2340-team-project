<<<<<<< HEAD
from django.shortcuts import render

def index(request):
    context = {
        'template_data': {'title': 'Applications - HireBuzz'}
    }
    return render(request, 'applications/index.html', context)
=======
from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'applications/index.html')


def about(request):
    return render(request, 'applications/about.html')
>>>>>>> c0c2653 (WIP)
