import re
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from getpass import getpass

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser'
    
    def handle(self, *args, **options):
        while True:
            email = input('Email: ').strip()
            if not email:
                self.stderr.write("Error: Email cannot be empty.")
            elif not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", email):
                self.stderr.write("Error: Invalid email format.")
            elif len(email) > 255:
                self.stderr.write("Error: Email cannot exceed 255 characters.")
            elif User.objects.filter(email=email).exists():
                self.stderr.write("Error: This email is already taken. Please choose a different one.")
            else:
                break

        while True:
            password = getpass('Password: ')
            confirm_password = getpass('Confirm Password: ')

            if not password:
                self.stderr.write("Error: Password cannot be empty.")
            elif password != confirm_password:
                self.stderr.write("Error: Passwords do not match.")
            elif len(password) > 128:
                self.stderr.write("Error: Password cannot exceed 128 characters.")
            else:
                break

        while True:
            name = input('Name: ').strip()
            if not name:
                self.stderr.write("Error: Name cannot be empty.")
            elif len(name) > 128:
                self.stderr.write("Error: Name cannot exceed 128 characters.")
            else:
                break

        while True:
            username = input('Username (optional): ').strip().lower()

            if username == "":
                break
            elif ' ' in username:
                self.stderr.write("Error: Username cannot contain spaces.")
            elif not re.match(r"^[a-z0-9_]+$", username):
                self.stderr.write("Error: Username can only contain lowercase letters, numbers, and underscores.")
            elif len(username) > 30:
                self.stderr.write("Error: Username cannot exceed 30 characters.")
            elif User.objects.filter(username=username).exists():
                self.stderr.write("Error: This username is already taken. Please choose a different one.")
            else:
                break

        while True:
            gender = input('Gender [male/female] (optional): ').strip().lower()

            if gender == "":
                break
            if gender not in ['male', 'female']:
                self.stderr.write("Error: Gender must be 'male' or 'female'.")
            elif len(gender) > 6:
                self.stderr.write("Error: Gender cannot exceed 6 characters.")
            else:
                break

        while True:
            phone = input('Phone (optional): ').strip()

            if phone == "":
                break
            elif not phone.isdigit():
                self.stderr.write("Error: Phone number must contain only digits.")
            elif len(phone) > 15:
                self.stderr.write("Error: Phone number cannot exceed 15 digits.")
            else:
                break

        while True:
            address = input('Address (optional): ').strip()
            if address == "":
                break
            elif len(address) > 255:
                self.stderr.write("Error: Address cannot exceed 255 characters.")
            else:
                break

        user = User.objects.create_superuser(
            email=email,
            username=username or None,
            password=password,
            name=name,
            gender=gender or None,
            address=address or None,
            phone=phone or None
        )

        if user:
            try:
                admin_group = Group.objects.get(name='admin')
                user.groups.add(admin_group)
                self.stdout.write(self.style.SUCCESS(f'Superuser "{email}" created successfully and assigned to the admin group.'))
            except Group.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Admin group does not exist. Superuser "{email}" was not assigned to the admin group.'))
        else:
            self.stdout.write(self.style.ERROR(f'Failed to create superuser "{email}".'))