from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from applications.models import Application


User = get_user_model()


class ApplicationStatusTrackingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', 'alice@example.com', 'password123')
        self.other_user = User.objects.create_user('bob', 'bob@example.com', 'password123')

    def test_application_defaults_to_applied(self):
        application = Application.objects.create(
            user=self.user,
            job_title='Backend Engineer',
            company_name='Acme Co'
        )

        self.assertEqual(application.status, Application.Status.APPLIED)

    def test_index_shows_only_current_user_applications(self):
        Application.objects.create(
            user=self.user,
            job_title='Backend Engineer',
            company_name='Acme',
            status=Application.Status.APPLIED
        )
        Application.objects.create(
            user=self.other_user,
            job_title='Data Scientist',
            company_name='Globex',
            status=Application.Status.INTERVIEW
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('applications:index'))

        self.assertContains(response, 'Backend Engineer')
        self.assertNotContains(response, 'Data Scientist')

    def test_user_can_update_status(self):
        application = Application.objects.create(
            user=self.user,
            job_title='Backend Engineer',
            company_name='Acme',
            status=Application.Status.APPLIED
        )

        self.client.force_login(self.user)
        response = self.client.post(
            reverse('applications:update_status', args=[application.pk]),
            {f'{application.pk}-status': Application.Status.INTERVIEW},
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        application.refresh_from_db()
        self.assertEqual(application.status, Application.Status.INTERVIEW)

    def test_create_view_respects_selected_status(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('applications:create'),
            {
                'job_title': 'Frontend Engineer',
                'company_name': 'Initech',
                'status': Application.Status.REVIEW,
                'notes': 'Portfolio sent'
            },
            follow=True
        )

        self.assertEqual(response.status_code, 200)
        application = Application.objects.get(user=self.user, job_title='Frontend Engineer')
        self.assertEqual(application.status, Application.Status.REVIEW)

    def test_user_cannot_update_someone_elses_application(self):
        application = Application.objects.create(
            user=self.other_user,
            job_title='Data Scientist',
            company_name='Globex',
            status=Application.Status.APPLIED
        )

        self.client.force_login(self.user)
        response = self.client.post(
            reverse('applications:update_status', args=[application.pk]),
            {f'{application.pk}-status': Application.Status.CLOSED}
        )

        self.assertEqual(response.status_code, 404)
        application.refresh_from_db()
        self.assertEqual(application.status, Application.Status.APPLIED)
