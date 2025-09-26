from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class RegistrationViewTests(TestCase):
    def test_get_registration_page(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Account')

    def test_successful_registration_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse('accounts:register'),
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'complex-pass123',
                'password2': 'complex-pass123',
            },
        )

        self.assertRedirects(response, reverse('profiles:create'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        # After registration, the user should be authenticated in the same session.
        self.assertEqual(int(self.client.session['_auth_user_id']), User.objects.get(username='newuser').id)
