from django.test import TestCase

from profiles.forms import ProfileForm


class ProfilePhoneValidationTests(TestCase):
    def _base_data(self, **overrides):
        data = {
            'headline': 'Engineer',
            'bio': 'Builder',
            'location': 'Atlanta',
            'phone': '4045551234',
            'skills': 'Python, Django',
            'education': 'BS Computer Science',
            'work_experience': '5 years experience',
            'linkedin_url': '',
            'github_url': '',
            'portfolio_url': '',
            'other_url': '',
            'is_public': True,
            'show_bio': True,
            'show_location': True,
            'show_phone': True,
            'show_education': True,
            'show_work_experience': True,
            'show_links': True,
        }
        data.update(overrides)
        return data

    def test_phone_must_be_ten_digits(self):
        form = ProfileForm(data=self._base_data(phone='56789029292020'))

        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)
        self.assertIn('10-digit', form.errors['phone'][0])

    def test_phone_allows_formatted_input_but_saves_digits(self):
        form = ProfileForm(data=self._base_data(phone='(404) 555-1234'))

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['phone'], '4045551234')
