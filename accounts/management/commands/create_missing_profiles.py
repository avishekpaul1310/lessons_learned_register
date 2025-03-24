# Create this file at: accounts/management/commands/create_missing_profiles.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = 'Creates profiles for users who do not have one'

    def create_default_image(self):
        """Create a default profile image and return it as ContentFile"""
        image_file = BytesIO()
        image = Image.new('RGB', (100, 100), color='gray')
        image.save(image_file, 'JPEG')
        image_file.seek(0)
        return ContentFile(image_file.read(), name='profile.jpg')

    def handle(self, *args, **kwargs):
        users_without_profiles = []
        
        # Find users without profiles
        for user in User.objects.all():
            try:
                # Check if profile exists
                user.profile
            except Profile.DoesNotExist:
                users_without_profiles.append(user)
        
        # Create missing profiles
        for user in users_without_profiles:
            self.stdout.write(f"Creating profile for user: {user.username}")
            profile = Profile(user=user)
            profile.job_title = f"Job Title"
            profile.department = f"Department"
            profile.image = self.create_default_image()
            
            # Save without calling the save method (which tries to resize the image)
            from django.db import models
            models.Model.save(profile)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(users_without_profiles)} profiles'))