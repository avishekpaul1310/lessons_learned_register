# accounts/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
import os

from .models import Profile
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm

class AccountsModelTests(TestCase):
    """Tests for the accounts models."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        # Create a profile manually since signals may not be connected in tests
        self.profile = Profile.objects.create(user=self.user)
        
    def test_profile_creation(self):
        """Test that a profile exists for a user."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.user, self.user)
        
    def test_profile_str(self):
        """Test the string representation of a profile."""
        self.assertEqual(str(self.user.profile), 'testuser Profile')
        
    def test_profile_save_with_image(self):
        """Test that images are handled on save."""
        # Create a test image
        image_file = BytesIO()
        image = Image.new('RGB', (500, 500), color='blue')
        image.save(image_file, 'jpeg')
        image_file.seek(0)
        
        # Create a temp directory for media if it doesn't exist
        media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media')
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)
        
        profile_pics_dir = os.path.join(media_dir, 'profile_pics')
        if not os.path.exists(profile_pics_dir):
            os.makedirs(profile_pics_dir)
        
        # Save the image to the profile
        test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=image_file.read(),
            content_type='image/jpeg'
        )
        
        # Try-except block to handle potential image processing errors in tests
        try:
            self.user.profile.image = test_image
            self.user.profile.save()
            
            # Check that the profile was saved
            profile = Profile.objects.get(user=self.user)
            self.assertIsNotNone(profile.image)
        except Exception as e:
            self.fail(f"Profile save with image failed: {str(e)}")


class AccountsFormTests(TestCase):
    """Tests for the accounts forms."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        # Create a profile manually
        self.profile = Profile.objects.create(user=self.user)
        
    def test_user_register_form_valid(self):
        """Test that the UserRegisterForm is valid with correct data."""
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complex-password123',
            'password2': 'complex-password123',
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_user_register_form_invalid(self):
        """Test that the UserRegisterForm is invalid with incorrect data."""
        # Test with mismatched passwords
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complex-password123',
            'password2': 'different-password',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        
        # Test with existing username
        form_data = {
            'username': 'testuser',  # Existing username
            'email': 'new@example.com',
            'password1': 'complex-password123',
            'password2': 'complex-password123',
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        
    def test_user_update_form_valid(self):
        """Test that the UserUpdateForm is valid with correct data."""
        form_data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'first_name': 'Test',
            'last_name': 'User',
        }
        form = UserUpdateForm(data=form_data, instance=self.user)
        self.assertTrue(form.is_valid())
        
    def test_profile_update_form_valid(self):
        """Test that the ProfileUpdateForm is valid with correct data."""
        # Create a test image
        image_file = BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(image_file, 'jpeg')
        image_file.seek(0)
        
        # Create a temp directory for media if it doesn't exist
        media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media')
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)
        
        profile_pics_dir = os.path.join(media_dir, 'profile_pics')
        if not os.path.exists(profile_pics_dir):
            os.makedirs(profile_pics_dir)
        
        # Test form with data
        form = ProfileUpdateForm(
            data={
                'job_title': 'Developer',
                'department': 'IT',
            },
            files={
                'image': SimpleUploadedFile(
                    name='test_image.jpg',
                    content=image_file.read(),
                    content_type='image/jpeg'
                )
            },
            instance=self.user.profile
        )
        self.assertTrue(form.is_valid())


class AccountsViewsTests(TestCase):
    """Tests for the accounts views."""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.profile_url = reverse('profile')
        self.logout_url = reverse('logout')
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        # Create a profile manually
        self.profile = Profile.objects.create(user=self.user)
        
        # Create test directories
        media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'media')
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)
        
        profile_pics_dir = os.path.join(media_dir, 'profile_pics')
        if not os.path.exists(profile_pics_dir):
            os.makedirs(profile_pics_dir)
        
    def test_register_view_get(self):
        """Test that the register view works correctly for GET requests."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        
    def test_register_view_post_valid(self):
        """Test that the register view works correctly for valid POST requests."""
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complex-password123',
            'password2': 'complex-password123',
        }
        response = self.client.post(self.register_url, form_data)
        
        # Check if user was created
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
        # Should redirect to login after successful registration
        self.assertRedirects(response, self.login_url)
        
    def test_register_view_post_invalid(self):
        """Test that the register view handles invalid POST requests correctly."""
        form_data = {
            'username': 'testuser',  # Existing username
            'email': 'new@example.com',
            'password1': 'complex-password123',
            'password2': 'complex-password123',
        }
        response = self.client.post(self.register_url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
        
    def test_profile_view_get_authenticated(self):
        """Test that authenticated users can access the profile view."""
        # Login the user
        self.client.login(username='testuser', password='testpassword')
        
        # Create default media directory and image if needed
        default_image_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'media', 'default.jpg'
        )
        if not os.path.exists(default_image_path):
            with open(default_image_path, 'wb') as f:
                # Create a simple image
                img = Image.new('RGB', (100, 100), color='gray')
                img_io = BytesIO()
                img.save(img_io, format='JPEG')
                f.write(img_io.getvalue())
        
        # Now access the profile page
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        
    def test_profile_view_get_unauthenticated(self):
        """Test that unauthenticated users are redirected from the profile view."""
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.profile_url}')
        
    def test_profile_view_post_valid(self):
        """Test that the profile view works correctly for valid POST requests."""
        # Login the user
        self.client.login(username='testuser', password='testpassword')
        
        # Create a test image
        image_file = BytesIO()
        image = Image.new('RGB', (100, 100), color='blue')
        image.save(image_file, 'jpeg')
        image_file.seek(0)
        
        # Create default media directory and image if needed
        default_image_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'media', 'default.jpg'
        )
        if not os.path.exists(default_image_path):
            with open(default_image_path, 'wb') as f:
                # Create a simple image
                img = Image.new('RGB', (100, 100), color='gray')
                img_io = BytesIO()
                img.save(img_io, format='JPEG')
                f.write(img_io.getvalue())
        
        form_data = {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'job_title': 'Developer',
            'department': 'IT',
        }
        
        files = {
            'image': SimpleUploadedFile(
                name='test_image.jpg',
                content=image_file.read(),
                content_type='image/jpeg'
            )
        }
        
        response = self.client.post(self.profile_url, data=form_data, files=files)
        
        # Should redirect back to profile
        self.assertEqual(response.status_code, 302)
        
        # Refresh user from database
        self.user.refresh_from_db()
        self.user.profile.refresh_from_db()
        
        # Check that the profile fields were updated
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.email, 'updated@example.com')
        
    def test_logout_view(self):
        """Test that the logout view works correctly."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/logout.html')
        
        # Verify that the user is logged out
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.profile_url}')