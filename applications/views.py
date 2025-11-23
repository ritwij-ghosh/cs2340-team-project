from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from applications.forms import ApplicationForm, ApplicationStatusForm
from applications.models import Application


@login_required
def index(request):
    applications = Application.objects.filter(user=request.user)
    status_steps = Application.Status.choices
    application_forms = [
        (application, ApplicationStatusForm(instance=application, prefix=str(application.id)))
        for application in applications
    ]
    context = {
        'applications': applications,
        'application_forms': application_forms,
        'status_steps': status_steps,
        'template_data': {'title': 'My Applications - HireBuzz'}
    }
    return render(request, 'applications/index.html', context)


@login_required
def create_application(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            messages.success(request, 'Application added! Track its progress below.')
            return redirect('applications:index')
    else:
        form = ApplicationForm()

    context = {
        'form': form,
        'template_data': {'title': 'Add Application - HireBuzz'}
    }
    return render(request, 'applications/create_application.html', context)


@login_required
def update_status(request, pk):
    application = get_object_or_404(Application, pk=pk, user=request.user)
    if request.method != 'POST':
        return redirect('applications:index')

    form = ApplicationStatusForm(request.POST, instance=application, prefix=str(application.id))
    if form.is_valid():
        form.save()
        messages.success(request, f'Status moved to {application.get_status_display()} for {application.job_title}.')
    else:
        messages.error(request, 'Could not update status. Please choose a valid option.')
    return redirect('applications:index')


@login_required
def quick_apply(request):
    if request.method != 'POST':
        messages.error(request, 'Invalid request method for quick apply.')
        return redirect('jobs:index')

    job_id = request.POST.get('job_id')
    job_title = (request.POST.get('job_title') or '').strip()
    company_name = (request.POST.get('company_name') or '').strip()
    note = (request.POST.get('note') or '').strip()

    if not job_title or not company_name:
        messages.error(request, 'Job title and company are required to apply.')
        return redirect('jobs:index')

    # Try to get the actual job if job_id is provided
    job_instance = None
    if job_id:
        try:
            from jobs.models import Job
            job_instance = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            pass

    try:
        application = Application.objects.create(
            user=request.user,
            job=job_instance,
            job_title=job_title,
            company_name=company_name,
            notes=note
        )
        
        # Create a message to the recruiter about the application
        from communications.models import Message
        from django.contrib.auth.models import User
        
        # Find the recruiter who posted this job
        recruiter = None
        if job_instance and job_instance.recruiter:
            recruiter = job_instance.recruiter
        else:
            # Fallback: Try to find the recruiter by company name
            recruiter = User.objects.filter(
                user_profile__user_type='recruiter',
                user_profile__company__icontains=company_name
            ).first()
        
        if recruiter:
            # Create message about the application
            message_subject = f"New Application for {job_title}"
            message_body = f"Hello,\n\nI have applied for the {job_title} position at {company_name}."
            
            if note:
                message_body += f"\n\nPersonalized Note:\n{note}"
            
            message_body += f"\n\nBest regards,\n{request.user.get_full_name() or request.user.username}"
            
            Message.objects.create(
                sender=request.user,
                recipient=recruiter,
                subject=message_subject,
                body=message_body
            )
        
        messages.success(request, f'Applied to {job_title} at {company_name}.')
    except IntegrityError:
        # Likely duplicate for today due to unique_together including applied_on
        existing = Application.objects.filter(
            user=request.user,
            job_title=job_title,
            company_name=company_name,
            applied_on__isnull=False
        ).order_by('-applied_on').first()
        messages.info(request, f'You have already applied to {job_title} at {company_name} today.')
        if existing and note:
            # Append note to existing record so the personalized note is not lost
            existing.notes = (existing.notes + '\n' if existing.notes else '') + note
            existing.save(update_fields=['notes', 'updated_at'])
    return redirect('applications:index')


@login_required
def kanban_board(request):
    """Display Kanban board for recruiters to manage applications by company."""
    # Only allow recruiters to view the Kanban board
    try:
        user_profile = request.user.user_profile
        if not user_profile.is_recruiter():
            messages.warning(request, 'Only recruiters can view the Kanban board.')
            return redirect('jobs:index')
        
        company = user_profile.company
        if not company:
            messages.warning(request, 'Please set your company in your profile to view the Kanban board.')
            return redirect('accounts:index')
    except:
        messages.warning(request, 'Please complete your profile setup first.')
        return redirect('accounts:index')
    
    # Get all applications for jobs posted by recruiters from the same company
    # OR applications where company_name matches the recruiter's company
    from jobs.models import Job
    
    # Get all jobs posted by recruiters from the same company
    # Also match jobs where the job's company field matches
    company_jobs = Job.objects.filter(
        Q(recruiter__user_profile__company=company) | Q(company__iexact=company)
    )
    
    # Get applications that match:
    # 1. Applications linked to jobs from this company
    # 2. Applications where company_name matches this company (case-insensitive)
    applications = Application.objects.filter(
        Q(job__in=company_jobs) | Q(company_name__iexact=company)
    ).select_related('user', 'job').order_by('-updated_at')
    
    # Organize applications by status
    status_columns = {}
    for status_code, status_label in Application.Status.choices:
        status_columns[status_code] = {
            'label': status_label,
            'applications': [app for app in applications if app.status == status_code],
            'badge_class': Application.STATUS_BADGE_CLASSES.get(status_code, 'bg-secondary text-dark')
        }
    
    context = {
        'template_data': {'title': f'Applicant Pipeline - {company} - HireBuzz'},
        'status_columns': status_columns,
        'company': company,
        'total_applications': applications.count(),
    }
    return render(request, 'applications/kanban_board.html', context)


@login_required
@require_http_methods(["POST"])
def update_application_status_ajax(request, pk):
    """API endpoint to update application status via AJAX (for drag-and-drop)."""
    try:
        user_profile = request.user.user_profile
        if not user_profile.is_recruiter():
            return JsonResponse({'success': False, 'error': 'Only recruiters can update application status.'}, status=403)
        
        company = user_profile.company
        if not company:
            return JsonResponse({'success': False, 'error': 'Company not set in profile.'}, status=400)
        
        application = get_object_or_404(Application, pk=pk)
        
        # Verify the application belongs to the recruiter's company
        from jobs.models import Job
        company_jobs = Job.objects.filter(
            Q(recruiter__user_profile__company=company) | Q(company__iexact=company)
        )
        
        if application.job and application.job not in company_jobs:
            if application.company_name.lower() != company.lower():
                return JsonResponse({'success': False, 'error': 'You can only update applications for your company.'}, status=403)
        
        # Also check if company_name matches (case-insensitive)
        if not application.job and application.company_name.lower() != company.lower():
            return JsonResponse({'success': False, 'error': 'You can only update applications for your company.'}, status=403)
        
        # Get new status from request
        new_status = request.POST.get('status')
        if not new_status:
            return JsonResponse({'success': False, 'error': 'Status is required.'}, status=400)
        
        # Validate status
        valid_statuses = [choice[0] for choice in Application.Status.choices]
        if new_status not in valid_statuses:
            return JsonResponse({'success': False, 'error': 'Invalid status.'}, status=400)
        
        # Update status
        application.status = new_status
        application.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Status updated to {application.get_status_display()}',
            'status': application.status,
            'status_display': application.get_status_display(),
            'badge_class': application.status_badge_class
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
