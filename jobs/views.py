<<<<<<< HEAD
from django.shortcuts import render

def index(request):
    context = {
        'template_data': {'title': 'Jobs - HireBuzz'}
    }
    return render(request, 'jobs/index.html', context)
=======
from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'jobs/index.html')


def about(request):
    return render(request, 'jobs/about.html')
>>>>>>> c0c2653 (WIP)
