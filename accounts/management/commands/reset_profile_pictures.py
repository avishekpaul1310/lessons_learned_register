from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from django.conf import settings
import os
import shutil

class Command(BaseCommand):
    help = 'Reset all profile pictures to use the default image'

    def handle(self, *args, **kwargs):
        # Get the path to the default profile image
        default_image_path = os.path.join(settings.MEDIA_ROOT, 'profile_pics', 'default.jpg')
        
        # Make sure the default image exists
        if not os.path.exists(default_image_path):
            self.stdout.write(self.style.ERROR('Default profile image not found at: %s' % default_image_path))
            return
            
        # Get all profiles
        profiles = Profile.objects.all()
        count = 0
        
        # Update each profile
        for profile in profiles:
            old_path = None
            if profile.image and hasattr(profile.image, 'path'):
                old_path = profile.image.path
            
            # Set to default image
            profile.image = 'profile_pics/default.jpg'
            profile.save(update_fields=['image'])
            count += 1
            
            # Log what we're doing
            if old_path:
                self.stdout.write(f'Updated profile for {profile.user.username} from {old_path} to default')
            else:
                self.stdout.write(f'Updated profile for {profile.user.username} to default')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully reset {count} profile pictures'))