from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction

from profiles.models import Profile


class Command(BaseCommand):
    help = 'Create demo candidate profiles for showcasing saved searches.'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Candidate 1: Guilherme Luvielmo (Atlanta, GA, Python/Data/Geo)
            g_user, _ = User.objects.get_or_create(
                username='guilherme.luvielmo',
                defaults={
                    'email': 'guilherme.luvielmo@example.com',
                    'first_name': 'Guilherme',
                    'last_name': 'Luvielmo',
                }
            )
            if not g_user.has_usable_password():
                g_user.set_password('DemoPass123!')
                g_user.save()
            Profile.objects.update_or_create(
                user=g_user,
                defaults={
                    'headline': 'Senior Data Engineer & GIS Specialist',
                    'bio': 'Building reliable data platforms with spatial analytics and Python.',
                    'location': 'Atlanta, GA',
                    'skills': 'Python, Django, PostGIS, Airflow, AWS, ETL, Pandas, GeoPandas',
                    'education': 'MS Computer Science',
                    'work_experience': 'Led ETL pipelines, spatial joins, and streaming ingestion.',
                    'linkedin_url': '',
                    'github_url': '',
                    'portfolio_url': '',
                    'other_url': '',
                    'is_public': True,
                    'show_bio': True,
                    'show_location': True,
                    'show_phone': False,
                    'show_education': True,
                    'show_work_experience': True,
                    'show_links': True,
                }
            )

            # Candidate 2: Raphael Lafeldt (San Jose, CA, React/AI/Fullstack)
            r_user, _ = User.objects.get_or_create(
                username='raphael.lafeldt',
                defaults={
                    'email': 'raphael.lafeldt@example.com',
                    'first_name': 'Raphael',
                    'last_name': 'Lafeldt',
                }
            )
            if not r_user.has_usable_password():
                r_user.set_password('DemoPass123!')
                r_user.save()
            Profile.objects.update_or_create(
                user=r_user,
                defaults={
                    'headline': 'Full‑Stack Engineer (React/Next.js) with GenAI experience',
                    'bio': 'Delivers polished UX with performant APIs, vector DBs, and LLM tooling.',
                    'location': 'San Jose, CA',
                    'skills': 'React, Next.js, TypeScript, Node.js, Python, LangChain, Vector DB, LLMs',
                    'education': 'BS Computer Engineering',
                    'work_experience': 'Built AI-enabled apps, semantic search, and robust frontends.',
                    'linkedin_url': '',
                    'github_url': '',
                    'portfolio_url': '',
                    'other_url': '',
                    'is_public': True,
                    'show_bio': True,
                    'show_location': True,
                    'show_phone': False,
                    'show_education': True,
                    'show_work_experience': True,
                    'show_links': True,
                }
            )

            # Candidate 3: Alex Python (Atlanta, GA, Python/Backend)
            a_user, _ = User.objects.get_or_create(
                username='alex.python',
                defaults={
                    'email': 'alex.python@example.com',
                    'first_name': 'Alex',
                    'last_name': 'Python',
                }
            )
            if not a_user.has_usable_password():
                a_user.set_password('DemoPass123!')
                a_user.save()
            Profile.objects.update_or_create(
                user=a_user,
                defaults={
                    'headline': 'Backend Engineer (Python/Django)',
                    'bio': 'Builds APIs and data services in Django and FastAPI with PostgreSQL.',
                    'location': 'Atlanta, GA',
                    'skills': 'Python, Django, REST, PostgreSQL, Celery, Docker',
                    'education': 'BS Computer Science',
                    'work_experience': 'Implemented scalable REST APIs and background workers.',
                    'linkedin_url': '',
                    'github_url': '',
                    'portfolio_url': '',
                    'other_url': '',
                    'is_public': True,
                    'show_bio': True,
                    'show_location': True,
                    'show_phone': False,
                    'show_education': True,
                    'show_work_experience': True,
                    'show_links': True,
                }
            )

        self.stdout.write(self.style.SUCCESS('Demo candidates created/updated.'))


