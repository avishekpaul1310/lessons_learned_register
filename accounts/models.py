from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.jpg', upload_to='profile_pics')
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    def save(self, *args, **kwargs):
        # Check if this is a new profile without an image
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Process the image for resizing/cropping
        try:
            if self.image and hasattr(self.image, 'path') and os.path.exists(self.image.path):
                img = Image.open(self.image.path)
                
                # Ensure the image is a square by cropping to the center if necessary
                if img.width != img.height:
                    # Get the smaller dimension
                    min_dimension = min(img.width, img.height)
                    
                    # Calculate cropping coordinates to center the image
                    left = (img.width - min_dimension) // 2
                    top = (img.height - min_dimension) // 2
                    right = left + min_dimension
                    bottom = top + min_dimension
                    
                    # Crop to square
                    img = img.crop((left, top, right, bottom))
                
                # Resize to a standard profile size
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                
                img.save(self.image.path)
        except Exception as e:
            # Log the error but don't crash
            print(f"Error processing profile image: {e}")
            pass

class AllowedEmailDomain(models.Model):
    """Model for storing domains that are allowed for registration"""
    domain = models.CharField(max_length=100, unique=True, 
                             help_text="Domain name without @ (e.g., 'company.com')")
    description = models.CharField(max_length=255, blank=True,
                                 help_text="Optional description or organization name")
    is_active = models.BooleanField(default=True,
                                  help_text="If unchecked, this domain will not be allowed for registration")
    date_added = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['domain']
        verbose_name = "Allowed Email Domain"
        verbose_name_plural = "Allowed Email Domains"
    
    def __str__(self):
        return self.domain