<<<<<<< HEAD
from django.shortcuts import render

def index(request):
    context = {
        'template_data': {'title': 'Communications - HireBuzz'}
    }
    return render(request, 'communications/index.html', context)
=======
from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request, 'communications/index.html')


def about(request):
    return render(request, 'communications/about.html')
>>>>>>> c0c2653 (WIP)
