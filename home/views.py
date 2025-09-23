from django.shortcuts import render

def index(request):
    context = {
        'template_data': {'title': 'Home - HireBuzz'}
    }
    return render(request, 'home/index.html', context)
