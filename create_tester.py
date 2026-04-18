import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carrent.settings')
django.setup()

from django.contrib.auth.models import User

username = 'n2tester'
password = '@n2tester'

if not User.objects.filter(username=username).exists():
    User.objects.create_user(username=username, password=password, is_staff=True, is_superuser=True)
    print(f"User '{username}' created successfully.")
else:
    print(f"User '{username}' already exists.")
