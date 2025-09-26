from django.shortcuts import render
from .models import Job

def index(request):
    approved_jobs = Job.objects.filter(status=Job.ModerationStatus.APPROVED).order_by('-created_at')
    context = {
        'template_data': {'title': 'Jobs - HireBuzz'},
        'jobs': approved_jobs,
    }
    return render(request, 'jobs/index.html', context)
