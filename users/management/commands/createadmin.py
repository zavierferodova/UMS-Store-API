from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

class Command(BaseCommand):
    help = 'Creates a superuser with a predefined password and assigns to admin group.'

    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        
        user_data = {
            'email': 'admin@mail.com',
            'password': 'adminmimin',
            'username': 'admin',
            'name': 'Administrator'
        }

        if User.objects.filter(email=user_data['email']).exists():
            self.stdout.write(self.style.WARNING('User with this email already exists.'))
            return

        try:
            self.stdout.write('Creating admin user...')
            
            user = User.objects.create_superuser(**user_data)

            admin_group, _ = Group.objects.get_or_create(name='admin')
            user.groups.add(admin_group)

            self.stdout.write(self.style.SUCCESS('Admin user created successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))
