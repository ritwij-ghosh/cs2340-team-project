from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Job
from .forms import JobForm, JobSearchForm
from .utils import geocode_location


def index(request):
    """Display job listings with search and filter functionality."""
    form = JobSearchForm(request.GET)
    jobs = Job.objects.filter(status='active')

    if form.is_valid():
        search = form.cleaned_data.get('search')
        location = form.cleaned_data.get('location')
        skills = form.cleaned_data.get('skills')
        employment_type = form.cleaned_data.get('employment_type')
        work_type = form.cleaned_data.get('work_type')
        experience_level = form.cleaned_data.get('experience_level')
        salary_min = form.cleaned_data.get('salary_min')
        salary_max = form.cleaned_data.get('salary_max')
        visa_sponsorship = form.cleaned_data.get('visa_sponsorship')
        remote_only = form.cleaned_data.get('remote_only')

        # Text search across multiple fields
        if search:
            jobs = jobs.filter(
                Q(title__icontains=search) |
                Q(company__icontains=search) |
                Q(description__icontains=search) |
                Q(requirements__icontains=search) |
                Q(skills_required__icontains=search)
            )

        # Location filter
        if location:
            jobs = jobs.filter(location__icontains=location)

        # Skills filter
        if skills:
            skill_keywords = [skill.strip() for skill in skills.split(',') if skill.strip()]
            skill_query = Q()
            for skill in skill_keywords:
                skill_query |= (
                    Q(skills_required__icontains=skill) |
                    Q(requirements__icontains=skill) |
                    Q(description__icontains=skill)
                )
            jobs = jobs.filter(skill_query)

        # Employment type filter
        if employment_type:
            jobs = jobs.filter(employment_type=employment_type)

        # Work type filter
        if work_type:
            jobs = jobs.filter(work_type=work_type)

        # Experience level filter
        if experience_level:
            jobs = jobs.filter(experience_level=experience_level)

        # Salary range filters
        if salary_min:
            jobs = jobs.filter(
                Q(salary_min__gte=salary_min) | Q(salary_max__gte=salary_min)
            )

        if salary_max:
            jobs = jobs.filter(
                Q(salary_max__lte=salary_max) | Q(salary_min__lte=salary_max)
            )

        # Visa sponsorship filter
        if visa_sponsorship:
            jobs = jobs.filter(visa_sponsorship=True)

        # Remote work filter
        if remote_only:
            jobs = jobs.filter(work_type__in=['remote', 'hybrid'])

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


@login_required
def map_view(request):
    """Display jobs on an interactive map for job seekers."""
    # Only allow job seekers to view the map
    try:
        user_profile = request.user.user_profile
        if not user_profile.is_job_seeker():
            messages.warning(request, 'Only job seekers can view the job map.')
            return redirect('jobs:index')
    except:
        messages.warning(request, 'Please complete your profile setup first.')
        return redirect('profiles:create')
    
    # Get jobs with coordinates
    jobs_with_coords = Job.objects.filter(
        status='active',
        latitude__isnull=False,
        longitude__isnull=False
    ).exclude(location__in=['Remote', 'remote', 'Anywhere', 'anywhere'])
    
    # Prepare job data for the map
    jobs_data = []
    for job in jobs_with_coords:
        jobs_data.append({
            'id': job.id,
            'title': job.title,
            'company': job.company,
            'location': job.location,
            'latitude': float(job.latitude),
            'longitude': float(job.longitude),
            'employment_type': job.get_employment_type_display(),
            'work_type': job.get_work_type_display(),
            'salary_display': job.get_salary_display(),
            'url': job.get_absolute_url(),
            'skills': job.get_skills_list()[:3],  # First 3 skills
        })
    
    # Get user's location from profile only
    user_lat = None
    user_lon = None
    max_distance = request.GET.get('distance', '100')  # Default 100 miles
    
    # Get location from user's profile
    try:
        user_profile = request.user.profile
        if user_profile.location:
            from jobs.utils import geocode_location
            profile_lat, profile_lon = geocode_location(user_profile.location)
            if profile_lat and profile_lon:
                user_lat = profile_lat
                user_lon = profile_lon
    except:
        pass
    
    # Apply distance filtering if user location is available
    # Note: We'll pass all jobs to the template and let JavaScript handle distance filtering
    # This allows for dynamic distance filtering without page reloads
    
    # Check if user has location in profile
    has_profile_location = False
    try:
        user_profile = request.user.profile
        has_profile_location = bool(user_profile.location)
    except:
        pass
    
    context = {
        'template_data': {'title': 'Job Map - HireBuzz'},
        'jobs_data': jobs_data,
        'jobs_count': len(jobs_data),  # Total jobs with coordinates
        'user_lat': user_lat,
        'user_lon': user_lon,
        'max_distance': max_distance,
        'has_profile_location': has_profile_location,
    }
    return render(request, 'jobs/map.html', context)


def geocode_job(request, job_id):
    """API endpoint to geocode a specific job."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    job = get_object_or_404(Job, id=job_id)
    
    if job.has_coordinates():
        return JsonResponse({
            'success': True,
            'message': 'Job already has coordinates',
            'latitude': float(job.latitude),
            'longitude': float(job.longitude)
        })
    
    lat, lon = geocode_location(job.location)
    
    if lat is not None and lon is not None:
        job.latitude = lat
        job.longitude = lon
        job.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Job geocoded successfully',
            'latitude': lat,
            'longitude': lon
        })
    else:
        return JsonResponse({
            'success': False,
            'message': 'Failed to geocode location'
        }, status=400)


@login_required
def applicant_cluster_map(request):
    """Display clusters of applicants by location for recruiters."""
    # Only allow recruiters to view the applicant cluster map
    try:
        user_profile = request.user.user_profile
        if not user_profile.is_recruiter():
            messages.warning(request, 'Only recruiters can view the applicant cluster map.')
            return redirect('jobs:index')
    except:
        messages.warning(request, 'Please complete your profile setup first.')
        return redirect('profiles:create')
    
    # Get all job seekers with profiles and location data
    from profiles.models import Profile
    from accounts.models import UserProfile
    
    # Get job seekers with public profiles and location data
    job_seeker_profiles = Profile.objects.filter(
        is_public=True,
        show_location=True,
        location__isnull=False
    ).exclude(location__in=['', 'Remote', 'remote', 'Anywhere', 'anywhere'])
    
    # Prepare applicant data for clustering
    applicants_data = []
    location_counts = {}
    
    for profile in job_seeker_profiles:
        # Geocode the location
        lat, lon = geocode_location(profile.location)
        
        if lat is not None and lon is not None:
            # Count applicants by location for clustering
            location_key = f"{lat:.4f},{lon:.4f}"
            if location_key not in location_counts:
                location_counts[location_key] = {
                    'latitude': lat,
                    'longitude': lon,
                    'location': profile.location,
                    'count': 0,
                    'applicants': []
                }
            
            location_counts[location_key]['count'] += 1
            location_counts[location_key]['applicants'].append({
                'name': profile.user.get_full_name() or profile.user.username,
                'headline': profile.headline,
                'skills': profile.get_skills_list()[:3],  # First 3 skills
                'profile_url': f"/profiles/{profile.user.id}/"
            })
    
    # Convert to list for template
    for location_data in location_counts.values():
        applicants_data.append({
            'latitude': location_data['latitude'],
            'longitude': location_data['longitude'],
            'location': location_data['location'],
            'count': location_data['count'],
            'applicants': location_data['applicants']
        })
    
    # Sort by count (highest first)
    applicants_data.sort(key=lambda x: x['count'], reverse=True)
    
    context = {
        'template_data': {'title': 'Applicant Clusters - HireBuzz'},
        'applicants_data': applicants_data,
        'total_applicants': sum(data['count'] for data in applicants_data),
        'unique_locations': len(applicants_data),
    }
    return render(request, 'jobs/applicant_cluster_map.html', context)