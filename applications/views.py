from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

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
