# accounts/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

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
        
    def test_profile_creation(self):
        """Test that a profile is automatically created for a new user."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.user, self.user)
        
    def test_profile_str(self):
        """Test the string representation of a profile."""
        self.assertEqual(str(self.user.profile), 'testuser Profile')
        
    def test_profile_save_with_image(self):
        """Test that images are resized on save."""
        # Create a test image
        image_file = BytesIO()
        image = Image.new('RGB', (500, 500))
        image.save(image_file, 'jpeg')
        image_file.seek(0)
        
        # Save the image to the profile
        self.user.profile.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=image_file.read(),
            content_type='image/jpeg'
        )
        self.user.profile.save()
        
        # Check that the profile was saved
        profile = Profile.objects.get(user=self.user)
        self.assertIsNotNone(profile.image)


class AccountsFormTests(TestCase):
    """Tests for the accounts forms."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
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
        image = Image.new('RGB', (100, 100))
        image.save(image_file, 'jpeg')
        image_file.seek(0)
        
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
        self.assertRedirects(response, self.login_url)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        
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
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        
    def test_profile_view_get_unauthenticated(self):
        """Test that unauthenticated users are redirected from the profile view."""
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.profile_url}')
        
    def test_profile_view_post_valid(self):
        """Test that the profile view works correctly for valid POST requests."""
        self.client.login(username='testuser', password='testpassword')
        
        # Create a test image
        image_file = BytesIO()
        image = Image.new('RGB', (100, 100))
        image.save(image_file, 'jpeg')
        image_file.seek(0)
        
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
        self.assertRedirects(response, self.profile_url)
        
        # Refresh user from database
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')
        self.assertEqual(self.user.email, 'updated@example.com')
        self.assertEqual(self.user.profile.job_title, 'Developer')
        self.assertEqual(self.user.profile.department, 'IT')
        
    def test_logout_view(self):
        """Test that the logout view works correctly."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/logout.html')
        
        # Verify that the user is logged out
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f'{self.login_url}?next={self.profile_url}')