from django.shortcuts import render

def index(request):
    context = {
        'template_data': {'title': 'Communications - HireBuzz'}
    }
    return render(request, 'communications/index.html', context)
