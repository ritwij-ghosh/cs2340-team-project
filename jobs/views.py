from django.shortcuts import render

def index(request):
    context = {
        'template_data': {'title': 'Jobs - HireBuzz'}
    }
    return render(request, 'jobs/index.html', context)
