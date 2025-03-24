# integration_tests.py
# Run with: python manage.py test integration_tests

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import timedelta
import tempfile
import os
from io import BytesIO
from PIL import Image

from projects.models import Project, ProjectRole
from lessons.models import Category, Lesson, Attachment, Comment
from accounts.models import Profile

# Use in-memory file storage for tests
@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class IntegrationTests(TestCase):
    """Integration tests for the Lessons Learned System."""
    
    def setUp(self):
        # Create test users
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpassword',
            is_staff=True,
            is_superuser=True
        )
        
        self.manager = User.objects.create_user(
            username='manager',
            email='manager@example.com',
            password='managerpassword'
        )
        
        self.team_member = User.objects.create_user(
            username='team_member',
            email='team@example.com',
            password='teampassword'
        )
        
        # Ensure profiles exist for all users
        for user in [self.admin, self.manager, self.team_member]:
            if not hasattr(user, 'profile'):
                # Create test image
                image_file = BytesIO()
                image = Image.new('RGB', (100, 100), color='gray')
                image.save(image_file, 'JPEG')
                image_file.seek(0)
                
                profile = Profile(user=user)
                profile.job_title = f"{user.username.title()} Job"
                profile.department = "Test Department"
                profile.image = SimpleUploadedFile(
                    name='test_image.jpg',
                    content=image_file.read(),
                    content_type='image/jpeg'
                )
                profile.save()
        
        # Create test categories
        self.categories = []
        for name in ['Technical', 'Process', 'Communication']:
            category = Category.objects.create(
                name=name,
                description=f"Description for {name} category"
            )
            self.categories.append(category)
        
        # Create test projects
        self.project1 = Project.objects.create(
            name='Project Alpha',
            description='This is Project Alpha description',
            start_date=timezone.now().date() - timedelta(days=30),
            end_date=timezone.now().date() + timedelta(days=60),
            is_active=True,
            created_by=self.admin
        )
        
        self.project2 = Project.objects.create(
            name='Project Beta',
            description='This is Project Beta description',
            start_date=timezone.now().date() - timedelta(days=15),
            end_date=None,
            is_active=True,
            created_by=self.manager
        )
        
        # Set up project teams and roles
        self.project1.team_members.add(self.admin, self.manager, self.team_member)
        self.project2.team_members.add(self.admin, self.manager)
        
        ProjectRole.objects.create(user=self.admin, project=self.project1, role='OWNER')
        ProjectRole.objects.create(user=self.manager, project=self.project1, role='MANAGER')
        ProjectRole.objects.create(user=self.team_member, project=self.project1, role='MEMBER')
        
        ProjectRole.objects.create(user=self.manager, project=self.project2, role='OWNER')
        ProjectRole.objects.create(user=self.admin, project=self.project2, role='VIEWER')
        
        self.client = Client()
    
    def test_end_to_end_workflow(self):
        """Test a complete workflow: login, create lesson, comment, star, and edit."""
        # 1. Login as manager
        login_success = self.client.login(username='manager', password='managerpassword')
        self.assertTrue(login_success)
        
        # 2. View the dashboard
        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertContains(dashboard_response, 'Dashboard')
        self.assertContains(dashboard_response, 'Project Alpha')
        self.assertContains(dashboard_response, 'Project Beta')
        
        # 3. Create a new lesson
        lesson_data = {
            'project': self.project1.id,
            'title': 'Improve Communication Process',
            'category': self.categories[2].id,  # Communication
            'date_identified': timezone.now().date().strftime('%Y-%m-%d'),
            'description': '<p>We need better communication processes.</p>',
            'recommendations': '<p>Implement daily standups and weekly retrospectives.</p>',
            'impact': 'HIGH',
            'status': 'NEW',
        }
        
        create_response = self.client.post(reverse('lesson-create'), lesson_data)
        self.assertEqual(create_response.status_code, 302)  # Redirect after success
        
        # Get the newly created lesson
        lesson = Lesson.objects.get(title='Improve Communication Process')
        self.assertIsNotNone(lesson)
        self.assertEqual(lesson.submitted_by, self.manager)
        
        # 4. View the lesson detail
        detail_url = reverse('lesson-detail', args=[lesson.id])
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'Improve Communication Process')
        self.assertContains(detail_response, 'daily standups')
        
        # 5. Add a comment to the lesson
        comment_data = {
            'text': 'Great insight! Let\'s implement this immediately.'
        }
        comment_response = self.client.post(detail_url, comment_data)
        self.assertEqual(comment_response.status_code, 302)  # Redirect after success
        
        # Verify the comment was added
        self.assertTrue(Comment.objects.filter(
            lesson=lesson,
            text='Great insight! Let\'s implement this immediately.',
            author=self.manager
        ).exists())
        
        # 6. Star the lesson
        star_url = f"{detail_url}?star=1"
        star_response = self.client.get(star_url)
        self.assertEqual(star_response.status_code, 302)  # Redirect after success
        
        # Verify the lesson was starred
        lesson.refresh_from_db()
        self.assertIn(self.manager, lesson.starred_by.all())
        
        # 7. Edit the lesson
        edit_url = reverse('lesson-update', args=[lesson.id])
        edit_data = {
            'project': self.project1.id,
            'title': 'Improve Communication Process - Updated',
            'category': self.categories[2].id,  # Communication
            'date_identified': timezone.now().date().strftime('%Y-%m-%d'),
            'description': '<p>We need better communication processes - updated.</p>',
            'recommendations': '<p>Implement daily standups and weekly retrospectives. Add documentation.</p>',
            'impact': 'HIGH',
            'status': 'IN_PROGRESS',
        }
        
        edit_response = self.client.post(edit_url, edit_data)
        self.assertEqual(edit_response.status_code, 302)  # Redirect after success
        
        # Verify the lesson was updated
        lesson.refresh_from_db()
        self.assertEqual(lesson.title, 'Improve Communication Process - Updated')
        self.assertEqual(lesson.status, 'IN_PROGRESS')
        
        # 8. Logout
        self.client.logout()
        
        # 9. Login as team member
        login_success = self.client.login(username='team_member', password='teampassword')
        self.assertTrue(login_success)
        
        # 10. View the lesson detail
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        
        # 11. Add another comment
        comment_data = {
            'text': 'I suggest adding a team chat tool as well.'
        }
        comment_response = self.client.post(detail_url, comment_data)
        self.assertEqual(comment_response.status_code, 302)  # Redirect after success
        
        # Verify the comment was added
        self.assertTrue(Comment.objects.filter(
            lesson=lesson,
            text='I suggest adding a team chat tool as well.',
            author=self.team_member
        ).exists())
        
        # 12. Try to edit the lesson (should be denied - not the submitter)
        edit_response = self.client.get(edit_url)
        self.assertEqual(edit_response.status_code, 302)  # Redirect with error
        
        # 13. Filter lessons
        filter_url = f"{reverse('lesson-list')}?status=IN_PROGRESS&impact=HIGH"
        filter_response = self.client.get(filter_url)
        self.assertEqual(filter_response.status_code, 200)
        self.assertContains(filter_response, 'Improve Communication Process - Updated')
        
    def test_project_team_management(self):
        """Test project creation and team management."""
        # 1. Login as admin
        login_success = self.client.login(username='admin', password='adminpassword')
        self.assertTrue(login_success)
        
        # 2. Create a new project
        project_data = {
            'name': 'Project Gamma',
            'description': 'This is Project Gamma description',
            'start_date': timezone.now().date().strftime('%Y-%m-%d'),
            'end_date': '',  # No end date
            'is_active': True,
        }
        
        create_response = self.client.post(reverse('project-create'), project_data)
        self.assertEqual(create_response.status_code, 302)  # Redirect after success
        
        # Get the newly created project
        project = Project.objects.get(name='Project Gamma')
        self.assertIsNotNone(project)
        self.assertEqual(project.created_by, self.admin)
        
        # Verify admin was automatically added as owner
        self.assertIn(self.admin, project.team_members.all())
        project_role = ProjectRole.objects.get(user=self.admin, project=project)
        self.assertEqual(project_role.role, 'OWNER')
        
        # 3. Add team_member to the project
        add_member_url = reverse('add-team-member', args=[project.id])
        member_data = {
            'user': self.team_member.id,
            'role': 'MEMBER',
        }
        
        add_member_response = self.client.post(add_member_url, member_data)
        self.assertEqual(add_member_response.status_code, 302)  # Redirect after success
        
        # Verify team_member was added to the project
        project.refresh_from_db()
        self.assertIn(self.team_member, project.team_members.all())
        project_role = ProjectRole.objects.get(user=self.team_member, project=project)
        self.assertEqual(project_role.role, 'MEMBER')
        
        # 4. Check project detail page
        detail_url = reverse('project-detail', args=[project.id])
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        self.assertContains(detail_response, 'Project Gamma')
        self.assertContains(detail_response, self.team_member.username)
        
        # 5. Logout and login as team_member
        self.client.logout()
        login_success = self.client.login(username='team_member', password='teampassword')
        self.assertTrue(login_success)
        
        # 6. Verify team_member can access the project
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, 200)
        
        # 7. Try to add a new member (should be denied - not owner/manager)
        add_member_response = self.client.get(add_member_url)
        self.assertEqual(add_member_response.status_code, 302)  # Redirect with error
    
    def test_dashboard_and_statistics(self):
        """Test dashboard and statistics functionality."""
        # 1. Create some lessons for testing statistics
        lesson1 = Lesson.objects.create(
            project=self.project1,
            title='Lesson 1',
            category=self.categories[0],
            date_identified=timezone.now().date(),
            description='Description 1',
            recommendations='Recommendations 1',
            impact='HIGH',
            status='NEW',
            submitted_by=self.admin
        )
        
        lesson2 = Lesson.objects.create(
            project=self.project1,
            title='Lesson 2',
            category=self.categories[1],
            date_identified=timezone.now().date() - timedelta(days=5),
            description='Description 2',
            recommendations='Recommendations 2',
            impact='MEDIUM',
            status='IMPLEMENTED',
            submitted_by=self.manager
        )
        
        lesson3 = Lesson.objects.create(
            project=self.project2,
            title='Lesson 3',
            category=self.categories[2],
            date_identified=timezone.now().date() - timedelta(days=10),
            description='Description 3',
            recommendations='Recommendations 3',
            impact='LOW',
            status='ARCHIVED',
            submitted_by=self.manager
        )
        
        # Star some lessons
        lesson1.starred_by.add(self.admin)
        lesson2.starred_by.add(self.admin)
        
        # 2. Login as admin
        login_success = self.client.login(username='admin', password='adminpassword')
        self.assertTrue(login_success)
        
        # 3. Check dashboard
        dashboard_response = self.client.get(reverse('dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)
        
        # Verify dashboard contains correct statistics
        self.assertContains(dashboard_response, 'Total Lessons')
        self.assertContains(dashboard_response, 'High Impact')
        self.assertContains(dashboard_response, 'Implemented')
        
        # Verify latest lessons section
        self.assertContains(dashboard_response, 'Lesson 1')
        self.assertContains(dashboard_response, 'Lesson 2')
        
        # Verify starred lessons section
        self.assertContains(dashboard_response, 'Starred Lessons')
        self.assertContains(dashboard_response, 'Lesson 1')
        self.assertContains(dashboard_response, 'Lesson 2')
        
        # 4. Check project statistics
        project_detail_url = reverse('project-detail', args=[self.project1.id])
        project_response = self.client.get(project_detail_url)
        self.assertEqual(project_response.status_code, 200)
        
        # Project should show lesson statistics
        self.assertContains(project_response, 'Total Lessons')
        self.assertContains(project_response, 'Implemented')
        self.assertContains(project_response, 'High Impact')
    
    def test_export_functionality(self):
        """Test CSV and PDF export functionality."""
        # 1. Create some lessons for testing exports
        for i in range(5):
            Lesson.objects.create(
                project=self.project1,
                title=f'Export Lesson {i+1}',
                category=self.categories[i % len(self.categories)],
                date_identified=timezone.now().date() - timedelta(days=i),
                description=f'Description {i+1}',
                recommendations=f'Recommendations {i+1}',
                impact=['HIGH', 'MEDIUM', 'LOW'][i % 3],
                status=['NEW', 'ACKNOWLEDGED', 'IN_PROGRESS', 'IMPLEMENTED', 'ARCHIVED'][i],
                submitted_by=self.admin
            )
        
        # 2. Login as admin
        login_success = self.client.login(username='admin', password='adminpassword')
        self.assertTrue(login_success)
        
        # 3. Test CSV export
        csv_url = reverse('lesson-list') + '?export=csv'
        csv_response = self.client.get(csv_url)
        
        # Verify the response
        self.assertEqual(csv_response.status_code, 200)
        self.assertEqual(csv_response['Content-Type'], 'text/csv')
        self.assertTrue('attachment; filename="lessons_learned.csv"' in csv_response['Content-Disposition'])
        
        # Check CSV content
        content = csv_response.content.decode('utf-8')
        self.assertTrue('Project,Title,Category,Date Identified,Status,Impact,Description,Recommendations,Submitted By' in content)
        for i in range(5):
            self.assertTrue(f'Export Lesson {i+1}' in content)
        
        # 4. Test PDF export (which is actually HTML in this implementation)
        pdf_url = reverse('lesson-list') + '?export=pdf'
        pdf_response = self.client.get(pdf_url)
        
        # Verify the response
        self.assertEqual(pdf_response.status_code, 200)
        self.assertTrue('text/html' in pdf_response['Content-Type'])
        self.assertTrue('attachment; filename="lessons_learned.html"' in pdf_response['Content-Disposition'])
        
        # Check HTML content
        content = pdf_response.content.decode('utf-8')
        self.assertTrue('Lessons Learned Report' in content)
        for i in range(5):
            self.assertTrue(f'Export Lesson {i+1}' in content)
    
    def test_user_profile_management(self):
        """Test user profile management functionality."""
        # 1. Login as admin
        login_success = self.client.login(username='admin', password='adminpassword')
        self.assertTrue(login_success)
        
        # 2. Access profile page
        profile_response = self.client.get(reverse('profile'))
        self.assertEqual(profile_response.status_code, 200)
        self.assertContains(profile_response, 'Profile')
        
        # 3. Update profile
        # Create a test image
        image_file = BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(image_file, 'JPEG')
        image_file.seek(0)
        
        profile_data = {
            'username': 'admin',
            'email': 'admin_updated@example.com',
            'first_name': 'Admin',
            'last_name': 'User',
            'job_title': 'System Administrator',
            'department': 'IT Department',
        }
        
        files = {
            'image': SimpleUploadedFile(
                name='new_profile.jpg',
                content=image_file.read(),
                content_type='image/jpeg'
            )
        }
        
        update_response = self.client.post(reverse('profile'), data=profile_data, files=files)
        self.assertEqual(update_response.status_code, 302)  # Redirect after success
        
        # Verify profile updates
        self.admin.refresh_from_db()
        self.admin.profile.refresh_from_db()
        
        self.assertEqual(self.admin.email, 'admin_updated@example.com')
        self.assertEqual(self.admin.first_name, 'Admin')
        self.assertEqual(self.admin.last_name, 'User')
        self.assertEqual(self.admin.profile.job_title, 'System Administrator')
        self.assertEqual(self.admin.profile.department, 'IT Department')
    
    def test_permission_boundaries(self):
        """Test permission boundaries across different user roles."""
        # Create test objects
        lesson = Lesson.objects.create(
            project=self.project1,
            title='Permission Test Lesson',
            category=self.categories[0],
            date_identified=timezone.now().date(),
            description='Permission test description',
            recommendations='Permission test recommendations',
            impact='MEDIUM',
            status='NEW',
            submitted_by=self.admin
        )
        
        # 1. Test as team_member (lowest permissions)
        self.client.login(username='team_member', password='teampassword')
        
        # Can view lessons in their project
        detail_response = self.client.get(reverse('lesson-detail', args=[lesson.id]))
        self.assertEqual(detail_response.status_code, 200)
        
        # Cannot edit lessons they didn't create
        edit_response = self.client.get(reverse('lesson-update', args=[lesson.id]))
        self.assertEqual(edit_response.status_code, 302)  # Redirect with error
        
        # Cannot delete lessons they didn't create
        delete_response = self.client.get(reverse('lesson-delete', args=[lesson.id]))
        self.assertEqual(delete_response.status_code, 302)  # Redirect with error
        
        # Cannot access projects they're not part of
        project2_response = self.client.get(reverse('project-detail', args=[self.project2.id]))
        self.assertEqual(project2_response.status_code, 302)  # Redirect with error
        
        # 2. Test as project manager
        self.client.logout()
        self.client.login(username='manager', password='managerpassword')
        
        # Can access both projects (as owner or manager)
        project1_response = self.client.get(reverse('project-detail', args=[self.project1.id]))
        self.assertEqual(project1_response.status_code, 200)
        
        project2_response = self.client.get(reverse('project-detail', args=[self.project2.id]))
        self.assertEqual(project2_response.status_code, 200)
        
        # Can add team members to projects they own or manage
        add_member_url = reverse('add-team-member', args=[self.project1.id])
        add_member_response = self.client.get(add_member_url)
        self.assertEqual(add_member_response.status_code, 200)
        
        # 3. Test staff permissions
        self.client.logout()
        self.client.login(username='admin', password='adminpassword')
        
        # Staff can edit any lesson
        edit_response = self.client.get(reverse('lesson-update', args=[lesson.id]))
        self.assertEqual(edit_response.status_code, 200)