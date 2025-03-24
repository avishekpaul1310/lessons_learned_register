# lessons/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
import tempfile
import os

from projects.models import Project, ProjectRole
from lessons.models import Category, Lesson, Attachment, Comment
from lessons.forms import LessonForm, AttachmentForm, CommentForm
from lessons.filters import LessonFilter

class LessonsModelTests(TestCase):
    """Tests for the lessons models."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            description='This is a test project',
            start_date=timezone.now().date(),
            created_by=self.user
        )
        self.project.team_members.add(self.user)
        
        self.category = Category.objects.create(
            name='Test Category',
            description='This is a test category'
        )
        
        self.lesson = Lesson.objects.create(
            project=self.project,
            category=self.category,
            title='Test Lesson',
            date_identified=timezone.now().date(),
            description='This is a test lesson description',
            recommendations='These are test recommendations',
            impact='MEDIUM',
            status='NEW',
            submitted_by=self.user
        )
        
        # Create a temporary file for attachment tests
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        self.temp_file.write(b'Test file content')
        self.temp_file.close()
        
        self.attachment = Attachment.objects.create(
            lesson=self.lesson,
            file=SimpleUploadedFile(
                name=os.path.basename(self.temp_file.name),
                content=open(self.temp_file.name, 'rb').read()
            ),
            uploaded_by=self.user,
            description='Test attachment'
        )
        
        self.comment = Comment.objects.create(
            lesson=self.lesson,
            author=self.user,
            text='This is a test comment'
        )
        
    def tearDown(self):
        # Clean up temporary file
        try:
            os.unlink(self.temp_file.name)
        except:
            pass
        
    def test_category_creation(self):
        """Test that a category can be created with all fields."""
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(self.category.description, 'This is a test category')
        
    def test_category_str(self):
        """Test the string representation of a category."""
        self.assertEqual(str(self.category), 'Test Category')
        
    def test_lesson_creation(self):
        """Test that a lesson can be created with all fields."""
        self.assertEqual(self.lesson.title, 'Test Lesson')
        self.assertEqual(self.lesson.project, self.project)
        self.assertEqual(self.lesson.category, self.category)
        self.assertEqual(self.lesson.description, 'This is a test lesson description')
        self.assertEqual(self.lesson.recommendations, 'These are test recommendations')
        self.assertEqual(self.lesson.impact, 'MEDIUM')
        self.assertEqual(self.lesson.status, 'NEW')
        self.assertEqual(self.lesson.submitted_by, self.user)
        
    def test_lesson_str(self):
        """Test the string representation of a lesson."""
        self.assertEqual(
            str(self.lesson), 
            f'Test Lesson ({self.project.name})'
        )
        
    def test_attachment_creation(self):
        """Test that an attachment can be created with all fields."""
        self.assertEqual(self.attachment.lesson, self.lesson)
        self.assertEqual(self.attachment.uploaded_by, self.user)
        self.assertEqual(self.attachment.description, 'Test attachment')
        self.assertIsNotNone(self.attachment.file)
        
    def test_attachment_str(self):
        """Test the string representation of an attachment."""
        self.assertEqual(
            str(self.attachment), 
            f'Attachment for {self.lesson.title}'
        )
        
    def test_comment_creation(self):
        """Test that a comment can be created with all fields."""
        self.assertEqual(self.comment.lesson, self.lesson)
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.text, 'This is a test comment')
        
    def test_comment_str(self):
        """Test the string representation of a comment."""
        self.assertEqual(
            str(self.comment), 
            f'Comment by {self.user.username} on {self.lesson.title}'
        )
        
    def test_lesson_tags_and_stars(self):
        """Test that users can be tagged in and star lessons."""
        # Create another user
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpassword'
        )
        
        # Add user2 to project
        self.project.team_members.add(user2)
        
        # Tag and star the lesson
        self.lesson.tags.add(user2)
        self.lesson.starred_by.add(user2)
        
        self.assertIn(user2, self.lesson.tags.all())
        self.assertIn(user2, self.lesson.starred_by.all())


class LessonsFormTests(TestCase):
    """Tests for the lessons forms."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            description='This is a test project',
            start_date=timezone.now().date(),
            created_by=self.user
        )
        self.project.team_members.add(self.user)
        
        self.category = Category.objects.create(
            name='Test Category',
            description='This is a test category'
        )
        
        # Create another user
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpassword'
        )
        self.project.team_members.add(self.user2)
        
    def test_lesson_form_valid(self):
        """Test that the LessonForm is valid with correct data."""
        form_data = {
            'project': self.project.id,
            'title': 'New Lesson',
            'category': self.category.id,
            'date_identified': timezone.now().date(),
            'description': 'This is a new lesson description',
            'recommendations': 'These are new recommendations',
            'impact': 'MEDIUM',
            'status': 'NEW',
            'tagged_users': [self.user2.id],
        }
        form = LessonForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())
        
    def test_lesson_form_invalid(self):
        """Test that the LessonForm is invalid with incorrect data."""
        # Test with missing required field
        form_data = {
            'project': self.project.id,
            'category': self.category.id,
            'date_identified': timezone.now().date(),
            'description': 'This is a new lesson description',
            'recommendations': 'These are new recommendations',
            'impact': 'MEDIUM',
            'status': 'NEW',
        }
        form = LessonForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        
    def test_attachment_form_valid(self):
        """Test that the AttachmentForm is valid with correct data."""
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
        temp_file.write(b'Test file content')
        temp_file.close()
        
        try:
            form = AttachmentForm(
                data={'description': 'Test attachment'},
                files={
                    'file': SimpleUploadedFile(
                        name=os.path.basename(temp_file.name),
                        content=open(temp_file.name, 'rb').read()
                    )
                }
            )
            self.assertTrue(form.is_valid())
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file.name)
            except:
                pass
        
    def test_comment_form_valid(self):
        """Test that the CommentForm is valid with correct data."""
        form_data = {
            'text': 'This is a test comment',
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_comment_form_invalid(self):
        """Test that the CommentForm is invalid with incorrect data."""
        # Test with empty text field
        form_data = {
            'text': '',
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('text', form.errors)


class LessonsViewsTests(TestCase):
    """Tests for the lessons views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.project = Project.objects.create(
            name='Test Project',
            description='This is a test project',
            start_date=timezone.now().date(),
            created_by=self.user
        )
        self.project.team_members.add(self.user)
        
        self.category = Category.objects.create(
            name='Test Category',
            description='This is a test category'
        )
        
        self.lesson = Lesson.objects.create(
            project=self.project,
            category=self.category,
            title='Test Lesson',
            date_identified=timezone.now().date(),
            description='This is a test lesson description',
            recommendations='These are test recommendations',
            impact='MEDIUM',
            status='NEW',
            submitted_by=self.user
        )
        
        # Create a comment
        self.comment = Comment.objects.create(
            lesson=self.lesson,
            author=self.user,
            text='This is a test comment'
        )
        
        # Create another user
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpassword'
        )
        
        # Create another project
        self.project2 = Project.objects.create(
            name='Test Project 2',
            description='This is another test project',
            start_date=timezone.now().date(),
            created_by=self.user2
        )
        self.project2.team_members.add(self.user2)
        
        # Create a lesson for the second user
        self.lesson2 = Lesson.objects.create(
            project=self.project2,
            category=self.category,
            title='Test Lesson 2',
            date_identified=timezone.now().date(),
            description='This is another test lesson description',
            recommendations='These are more test recommendations',
            impact='HIGH',
            status='ACKNOWLEDGED',
            submitted_by=self.user2
        )
        
        # Set up URLs
        self.lesson_list_url = reverse('lesson-list')
        self.lesson_detail_url = reverse('lesson-detail', args=[self.lesson.id])
        self.lesson_create_url = reverse('lesson-create')
        self.lesson_update_url = reverse('lesson-update', args=[self.lesson.id])
        self.lesson_delete_url = reverse('lesson-delete', args=[self.lesson.id])
        self.dashboard_url = reverse('dashboard')
        
    def test_lesson_list_view_authenticated(self):
        """Test that authenticated users can access the lesson list view."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.lesson_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lessons/lesson_list.html')
        self.assertContains(response, 'Test Lesson')
        
    def test_lesson_list_view_unauthenticated(self):
        """Test that unauthenticated users are redirected from the lesson list view."""
        response = self.client.get(self.lesson_list_url)
        self.assertRedirects(response, f'/login/?next={self.lesson_list_url}')
        
    def test_lesson_detail_view_authenticated_team_member(self):
        """Test that team members can access the lesson detail view."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.lesson_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lessons/lesson_detail.html')
        self.assertContains(response, 'Test Lesson')
        self.assertContains(response, 'This is a test comment')
        
    def test_lesson_detail_view_authenticated_non_team_member(self):
        """Test that non-team members cannot access the lesson detail view."""
        self.client.login(username='testuser2', password='testpassword')
        response = self.client.get(self.lesson_detail_url)
        # Should redirect with an error message
        self.assertEqual(response.status_code, 302)
        
    def test_lesson_create_view_get(self):
        """Test that the lesson create view works correctly for GET requests."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.lesson_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lessons/lesson_form.html')
        
    def test_lesson_create_view_post_valid(self):
        """Test that the lesson create view works correctly for valid POST requests."""
        self.client.login(username='testuser', password='testpassword')
        form_data = {
            'project': self.project.id,
            'title': 'New Lesson',
            'category': self.category.id,
            'date_identified': timezone.now().date(),
            'description': 'This is a new lesson description',
            'recommendations': 'These are new recommendations',
            'impact': 'MEDIUM',
            'status': 'NEW',
        }
        response = self.client.post(self.lesson_create_url, form_data)
        
        # Get the new lesson
        new_lesson = Lesson.objects.get(title='New Lesson')
        
        # Should redirect to the new lesson's detail page
        self.assertRedirects(response, reverse('lesson-detail', args=[new_lesson.id]))
        
        # Check that the lesson was created correctly
        self.assertEqual(new_lesson.description, 'This is a new lesson description')
        self.assertEqual(new_lesson.submitted_by, self.user)
        
    def test_lesson_update_view_get(self):
        """Test that the lesson update view works correctly for GET requests."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.lesson_update_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lessons/lesson_form.html')
        
    def test_lesson_update_view_post_valid(self):
        """Test that the lesson update view works correctly for valid POST requests."""
        self.client.login(username='testuser', password='testpassword')
        form_data = {
            'project': self.project.id,
            'title': 'Updated Lesson',
            'category': self.category.id,
            'date_identified': timezone.now().date(),
            'description': 'This is an updated lesson description',
            'recommendations': 'These are updated recommendations',
            'impact': 'HIGH',
            'status': 'ACKNOWLEDGED',
        }
        response = self.client.post(self.lesson_update_url, form_data)
        
        # Should redirect to the lesson's detail page
        self.assertRedirects(response, self.lesson_detail_url)
        
        # Check that the lesson was updated correctly
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, 'Updated Lesson')
        self.assertEqual(self.lesson.impact, 'HIGH')
        self.assertEqual(self.lesson.status, 'ACKNOWLEDGED')
        
    def test_lesson_update_view_non_submitter(self):
        """Test that non-submitters cannot update lessons."""
        # Add user2 to project1 to give them access
        self.project.team_members.add(self.user2)
        
        self.client.login(username='testuser2', password='testpassword')
        response = self.client.get(self.lesson_update_url)
        
        # Should redirect with an error message
        self.assertEqual(response.status_code, 302)
        
    def test_lesson_delete_view_submitter(self):
        """Test that submitters can delete their lessons."""
        self.client.login(username='testuser', password='testpassword')
        
        # First test GET request (confirmation page)
        response = self.client.get(self.lesson_delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lessons/confirm_delete.html')
        
        # Then test POST request (actual deletion)
        response = self.client.post(self.lesson_delete_url)
        
        # Should redirect to the project's detail page
        self.assertRedirects(response, reverse('project-detail', args=[self.project.id]))
        
        # Check that the lesson was deleted
        self.assertFalse(Lesson.objects.filter(id=self.lesson.id).exists())
        
    def test_lesson_delete_view_non_submitter(self):
        """Test that non-submitters cannot delete lessons."""
        # Add user2 to project1 to give them access
        self.project.team_members.add(self.user2)
        
        self.client.login(username='testuser2', password='testpassword')
        response = self.client.get(self.lesson_delete_url)
        
        # Should redirect with an error message
        self.assertEqual(response.status_code, 302)
        
    def test_add_comment(self):
        """Test that users can add comments to lessons."""
        self.client.login(username='testuser', password='testpassword')
        form_data = {
            'text': 'This is a new comment',
        }
        response = self.client.post(self.lesson_detail_url, form_data)
        
        # Should redirect to the lesson's detail page
        self.assertRedirects(response, self.lesson_detail_url)
        
        # Check that the comment was added
        self.assertTrue(Comment.objects.filter(
            lesson=self.lesson,
            text='This is a new comment',
            author=self.user
        ).exists())
        
    def test_star_lesson(self):
        """Test that users can star and unstar lessons."""
        self.client.login(username='testuser', password='testpassword')
        
        # Star the lesson
        star_url = f"{self.lesson_detail_url}?star=1"
        response = self.client.get(star_url)
        
        # Should redirect to the lesson's detail page
        self.assertRedirects(response, self.lesson_detail_url)
        
        # Check that the lesson was starred
        self.lesson.refresh_from_db()
        self.assertIn(self.user, self.lesson.starred_by.all())
        
        # Unstar the lesson
        response = self.client.get(star_url)
        
        # Should redirect to the lesson's detail page
        self.assertRedirects(response, self.lesson_detail_url)
        
        # Check that the lesson was unstarred
        self.lesson.refresh_from_db()
        self.assertNotIn(self.user, self.lesson.starred_by.all())
        
    def test_dashboard_view(self):
        """Test that the dashboard view works correctly."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lessons/dashboard.html')
        
        # Check that the dashboard contains key sections
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Latest Lessons')
        self.assertContains(response, 'Your Projects')
        
        # Check that the lesson is displayed
        self.assertContains(response, 'Test Lesson')
        
        # Check that statistics are correct
        self.assertContains(response, 'Total Lessons')


class LessonsFilterTests(TestCase):
    """Tests for the lessons filters."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )

        self.request = type('MockRequest', (), {'user': self.user})
        
        self.project1 = Project.objects.create(
            name='Project 1',
            description='This is project 1',
            start_date=timezone.now().date(),
            created_by=self.user
        )
        self.project1.team_members.add(self.user)
        
        self.project2 = Project.objects.create(
            name='Project 2',
            description='This is project 2',
            start_date=timezone.now().date(),
            created_by=self.user
        )
        self.project2.team_members.add(self.user)
        
        self.category1 = Category.objects.create(name='Category 1')
        self.category2 = Category.objects.create(name='Category 2')
        
        # Create lessons with different attributes
        self.lesson1 = Lesson.objects.create(
            project=self.project1,
            category=self.category1,
            title='High Impact Lesson',
            date_identified=timezone.now().date(),
            description='High impact description',
            recommendations='High impact recommendations',
            impact='HIGH',
            status='NEW',
            submitted_by=self.user
        )
        
        self.lesson2 = Lesson.objects.create(
            project=self.project1,
            category=self.category2,
            title='Medium Impact Lesson',
            date_identified=timezone.now().date() - timedelta(days=10),
            description='Medium impact description',
            recommendations='Medium impact recommendations',
            impact='MEDIUM',
            status='ACKNOWLEDGED',
            submitted_by=self.user
        )
        
        self.lesson3 = Lesson.objects.create(
            project=self.project2,
            category=self.category1,
            title='Low Impact Lesson',
            date_identified=timezone.now().date() - timedelta(days=20),
            description='Low impact description',
            recommendations='Low impact recommendations',
            impact='LOW',
            status='IMPLEMENTED',
            submitted_by=self.user
        )
        
        # Star a lesson
        self.lesson1.starred_by.add(self.user)
        
        # Create a mock request object for the filter
        self.request = type('MockRequest', (), {'user': self.user})
        
    def test_filter_by_project(self):
        """Test filtering lessons by project."""
        filter_data = {'project': self.project1.id}
        f = LessonFilter(filter_data, Lesson.objects.all(), request=self.request)
        
        self.assertEqual(f.qs.count(), 2)
        self.assertIn(self.lesson1, f.qs)
        self.assertIn(self.lesson2, f.qs)
        self.assertNotIn(self.lesson3, f.qs)
        
    def test_filter_by_category(self):
        """Test filtering lessons by category."""
        filter_data = {'category': self.category1.id}
        f = LessonFilter(filter_data, Lesson.objects.all(), request=self.request)
        
        self.assertEqual(f.qs.count(), 2)
        self.assertIn(self.lesson1, f.qs)
        self.assertNotIn(self.lesson2, f.qs)
        self.assertIn(self.lesson3, f.qs)
        
    def test_filter_by_status(self):
        """Test filtering lessons by status."""
        filter_data = {'status': 'NEW'}
        f = LessonFilter(filter_data, Lesson.objects.all(), request=self.request)
        
        self.assertEqual(f.qs.count(), 1)
        self.assertIn(self.lesson1, f.qs)
        self.assertNotIn(self.lesson2, f.qs)
        self.assertNotIn(self.lesson3, f.qs)
        
    def test_filter_by_impact(self):
        """Test filtering lessons by impact."""
        filter_data = {'impact': 'HIGH'}
        f = LessonFilter(filter_data, Lesson.objects.all(), request=self.request)
        
        self.assertEqual(f.qs.count(), 1)
        self.assertIn(self.lesson1, f.qs)
        self.assertNotIn(self.lesson2, f.qs)
        self.assertNotIn(self.lesson3, f.qs)
        
    def test_filter_by_date_range(self):
        """Test filtering lessons by date range."""
        today = timezone.now().date()
        filter_data = {
            'date_from': today - timedelta(days=15),
            'date_to': today,
        }
        f = LessonFilter(filter_data, Lesson.objects.all(), request=self.request)
        
        self.assertEqual(f.qs.count(), 2)
        self.assertIn(self.lesson1, f.qs)
        self.assertIn(self.lesson2, f.qs)
        self.assertNotIn(self.lesson3, f.qs)
        
    def test_filter_by_starred(self):
        """Test filtering lessons by starred status."""
        # Clear out any existing stars first
        for lesson in Lesson.objects.all():
            lesson.starred_by.clear()
    
        # Now star only the specific lesson we want to test
        self.lesson1.starred_by.add(self.user)

        self.request.user = self.user
    
        # Now test the filter
        filter_data = {'is_starred': True}
        f = LessonFilter(filter_data, Lesson.objects.all(), request=self.request)

        print(f"User in request: {self.request.user.username}")
        print(f"Lesson1 starred by: {[u.username for u in self.lesson1.starred_by.all()]}")
        print(f"Filter query count: {f.qs.count()}")
        print(f"Lessons in query: {[l.title for l in f.qs]}")
    
        self.assertEqual(f.qs.count(), 1)
        self.assertIn(self.lesson1, f.qs)
        self.assertNotIn(self.lesson2, f.qs)
        self.assertNotIn(self.lesson3, f.qs)
        
    def test_filter_by_title(self):
        """Test filtering lessons by title."""
        filter_data = {'title': 'High'}
        f = LessonFilter(filter_data, Lesson.objects.all(), request=self.request)
        
        self.assertEqual(f.qs.count(), 1)
        self.assertIn(self.lesson1, f.qs)
        self.assertNotIn(self.lesson2, f.qs)
        self.assertNotIn(self.lesson3, f.qs)
        
    def test_combined_filters(self):
        """Test combining multiple filters."""
        filter_data = {
            'project': self.project1.id,
            'impact': 'MEDIUM',
        }
        f = LessonFilter(filter_data, Lesson.objects.all(), request=self.request)
        
        self.assertEqual(f.qs.count(), 1)
        self.assertNotIn(self.lesson1, f.qs)
        self.assertIn(self.lesson2, f.qs)
        self.assertNotIn(self.lesson3, f.qs)
