from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job
from .forms import JobForm, JobSearchForm


def index(request):
    """Display job listings with search and filter functionality."""
    form = JobSearchForm(request.GET)
    jobs = Job.objects.filter(status='active')

    if form.is_valid():
        search = form.cleaned_data.get('search')
        location = form.cleaned_data.get('location')
        employment_type = form.cleaned_data.get('employment_type')
        experience_level = form.cleaned_data.get('experience_level')

        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(company__icontains=search) |
                Q(description__icontains=search)
            )

        if location:
            jobs = jobs.filter(location__icontains=location)

        if employment_type:
            jobs = jobs.filter(employment_type=employment_type)

        if experience_level:
            jobs = jobs.filter(experience_level=experience_level)

    context = {
        'template_data': {'title': 'Jobs - HireBuzz'},
        'jobs': jobs,
        'search_form': form,
    }
    return render(request, 'jobs/index.html', context)


def detail(request, pk):
    """Display job detail page."""
    job = get_object_or_404(Job, pk=pk, status='active')
    context = {
        'template_data': {'title': f'{job.title} at {job.company} - HireBuzz'},
        'job': job,
    }
    return render(request, 'jobs/detail.html', context)


@login_required
def post_job(request):
    """Allow recruiters to post new jobs."""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm()

    context = {
        'template_data': {'title': 'Post a Job - HireBuzz'},
        'form': form,
    }
    return render(request, 'jobs/post_job.html', context)


@login_required
def edit_job(request, pk):
    """Allow recruiters to edit their posted jobs."""
    job = get_object_or_404(Job, pk=pk, recruiter=request.user)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm(instance=job)

    context = {
        'template_data': {'title': f'Edit {job.title} - HireBuzz'},
        'form': form,
        'job': job,
    }
    return render(request, 'jobs/edit_job.html', context)


@login_required
def my_jobs(request):
    """Display jobs posted by the current user."""
    jobs = Job.objects.filter(recruiter=request.user).order_by('-created_at')
    context = {
        'template_data': {'title': 'My Posted Jobs - HireBuzz'},
        'jobs': jobs,
    }
    return render(request, 'jobs/my_jobs.html', context)


@login_required
def delete_job(request, pk):
    """Allow recruiters to delete their posted jobs."""
    job = get_object_or_404(Job, pk=pk, recruiter=request.user)

    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('jobs:my_jobs')

    context = {
        'template_data': {'title': f'Delete {job.title} - HireBuzz'},
        'job': job,
    }
    return render(request, 'jobs/delete_job.html', context)
