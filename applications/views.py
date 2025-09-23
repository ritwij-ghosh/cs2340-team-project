from django.shortcuts import render

def index(request):
    context = {
        'template_data': {'title': 'Applications - HireBuzz'}
    }
    return render(request, 'applications/index.html', context)
