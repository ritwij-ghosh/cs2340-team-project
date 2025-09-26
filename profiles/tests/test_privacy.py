from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from profiles.models import Profile


class ProfilePrivacyTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner', email='owner@example.com', password='pass1234'
        )
        self.other_user = User.objects.create_user(
            username='other', email='other@example.com', password='pass1234'
        )

    def _create_profile(self, **kwargs):
        defaults = {
            'headline': 'Software Engineer',
            'bio': 'Experienced engineer.',
            'location': 'Atlanta, GA',
            'phone': '555-555-5555',
            'skills': 'Python, Django',
            'education': 'BS Computer Science',
            'work_experience': 'Worked at Tech Corp.',
        }
        defaults.update(kwargs)
        return Profile.objects.create(user=self.owner, **defaults)

    def test_private_profile_hidden_from_other_users(self):
        profile = self._create_profile(is_public=False)

        self.client.force_login(self.other_user)
        response = self.client.get(reverse('profiles:view', args=[self.owner.id]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('profiles:index'))

        index_response = self.client.get(reverse('profiles:index'))
        self.assertEqual(index_response.status_code, 200)
        self.assertNotIn(profile, index_response.context['profiles'])

    def test_private_profile_visible_to_owner(self):
        self._create_profile(is_public=False)

        self.client.force_login(self.owner)
        response = self.client.get(reverse('profiles:view', args=[self.owner.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'You are previewing your profile')

    def test_has_public_links_respects_privacy_flag(self):
        profile = self._create_profile(
            show_links=False,
            linkedin_url='https://linkedin.com/in/example'
        )

        self.assertTrue(profile.has_links())
        self.assertFalse(profile.has_public_links())
