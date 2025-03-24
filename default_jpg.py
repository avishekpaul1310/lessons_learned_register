# create_default_jpg.py
# Save this in your project root

import os
from PIL import Image
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lessons_learned.settings')
django.setup()

from django.conf import settings

# Create media directory if it doesn't exist
media_dir = os.path.join(settings.BASE_DIR, 'media')
if not os.path.exists(media_dir):
    os.makedirs(media_dir)

# Create a default.jpg image
default_img_path = os.path.join(media_dir, 'default.jpg')
if not os.path.exists(default_img_path):
    # Generate a gray image as a placeholder
    img = Image.new('RGB', (100, 100), color='gray')
    img.save(default_img_path)
    print(f"Created default profile image at {default_img_path}")
else:
    print(f"Default profile image already exists at {default_img_path}")

# Create profile_pics directory if it doesn't exist
profile_pics_dir = os.path.join(media_dir, 'profile_pics')
if not os.path.exists(profile_pics_dir):
    os.makedirs(profile_pics_dir)
    print(f"Created profile_pics directory at {profile_pics_dir}")
else:
    print(f"Profile_pics directory already exists at {profile_pics_dir}")