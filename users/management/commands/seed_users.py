from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = 'Seeds the database with user data (excluding admin)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding users...')
        
        roles = ['procurement', 'cashier', 'checker']
        
        for role in roles:
            self.stdout.write(f'Creating users for role: {role}')
            email = f'{role}@mail.com'
            name = f'{role.capitalize()} User'
            username = role
            
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email,
                    password='password123',
                    username=username,
                    name=name,
                    role=role,
                    is_active=True
                )
                self.stdout.write(f'  Created user: {email}')
            else:
                self.stdout.write(f'  User already exists: {email}')

        self.stdout.write(self.style.SUCCESS('Successfully seeded users'))
