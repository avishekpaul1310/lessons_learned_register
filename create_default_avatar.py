import os
from PIL import Image, ImageDraw
import random

# Create a directory for profile pics if it doesn't exist
media_dir = os.path.join('media', 'profile_pics')
if not os.path.exists(media_dir):
    os.makedirs(media_dir)

def generate_default_avatar(size=300, bg_color=(240, 244, 248), circle_color=(70, 130, 180)):
    """Generate a default avatar with a light blue background and darker blue circle"""
    # Create a blank image with a light blue background
    img = Image.new('RGB', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw a darker blue circle in the center
    circle_radius = size // 3
    center_x, center_y = size // 2, size // 2
    left_top = (center_x - circle_radius, center_y - circle_radius)
    right_bottom = (center_x + circle_radius, center_y + circle_radius)
    draw.ellipse([left_top, right_bottom], fill=circle_color)
    
    # Save the default profile image
    default_profile_path = os.path.join(media_dir, 'default.jpg')
    img.save(default_profile_path)
    
    # Also save as profile.jpg for existing references
    profile_path = os.path.join(media_dir, 'profile.jpg')
    img.save(profile_path)
    
    print(f"Default avatar created at: {default_profile_path}")
    return default_profile_path

if __name__ == "__main__":
    # Generate default avatar
    default_path = generate_default_avatar()
    print(f"Generated default avatar at: {default_path}")