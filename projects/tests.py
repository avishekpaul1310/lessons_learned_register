# projects/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta

from .models import Project, ProjectRole
from .forms import ProjectForm, ProjectRoleForm

class ProjectsModelTests(TestCase):
    """Tests for the projects models."""
    
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
            end_date=timezone.now().date() + timedelta(days=30),
            is_active=True,
            created_by=self.user
        )
        self.project.team_members.add(self.user)
        
        self.project_role = ProjectRole.objects.create(
            user=self.user,
            project=self.project,
            role='OWNER'
        )
        
    def test_project_creation(self):
        """Test that a project can be created with all fields."""
        self.assertEqual(self.project.name, 'Test Project')
        self.assertEqual(self.project.description, 'This is a test project')
        self.assertEqual(self.project.created_by, self.user)
        self.assertTrue(self.project.is_active)
        self.assertIsNotNone(self.project.start_date)
        self.assertIsNotNone(self.project.end_date)
        self.assertIn(self.user, self.project.team_members.all())
        
    def test_project_str(self):
        """Test the string representation of a project."""
        self.assertEqual(str(self.project), 'Test Project')
        
    def test_project_role_creation(self):
        """Test that a project role can be created with all fields."""
        self.assertEqual(self.project_role.user, self.user)
        self.assertEqual(self.project_role.project, self.project)
        self.assertEqual(self.project_role.role, 'OWNER')
        
    def test_project_role_str(self):
        """Test the string representation of a project role."""
        self.assertEqual(
            str(self.project_role), 
            f'{self.user.username} - {self.project.name} - {self.project_role.role}'
        )
        
    def test_project_role_uniqueness(self):
        """Test that a user cannot have multiple roles in the same project."""
        # Attempt to create a duplicate role
        with self.assertRaises(Exception):
            ProjectRole.objects.create(
                user=self.user,
                project=self.project,
                role='MANAGER'
            )


class ProjectsFormTests(TestCase):
    """Tests for the projects forms."""
    
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
            end_date=timezone.now().date() + timedelta(days=30),
            is_active=True,
            created_by=self.user
        )
        
    def test_project_form_valid(self):
        """Test that the ProjectForm is valid with correct data."""
        form_data = {
            'name': 'New Project',
            'description': 'This is a new project',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=30),
            'is_active': True,
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_project_form_invalid(self):
        """Test that the ProjectForm is invalid with incorrect data."""
        # Test with missing required field
        form_data = {
            'description': 'This is a new project',
            'start_date': timezone.now().date(),
            'is_active': True,
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
    def test_project_role_form_valid(self):
        """Test that the ProjectRoleForm is valid with correct data."""
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpassword'
        )
        
        form_data = {
            'user': user2.id,
            'role': 'MEMBER',
        }
        form = ProjectRoleForm(data=form_data)
        self.assertTrue(form.is_valid())


class ProjectsViewsTests(TestCase):
    """Tests for the projects views."""
    
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
            end_date=timezone.now().date() + timedelta(days=30),
            is_active=True,
            created_by=self.user
        )
        self.project.team_members.add(self.user)
        
        self.project_role = ProjectRole.objects.create(
            user=self.user,
            project=self.project,
            role='OWNER'
        )
        
        self.project_list_url = reverse('project-list')
        self.project_detail_url = reverse('project-detail', args=[self.project.id])
        self.project_create_url = reverse('project-create')
        self.add_team_member_url = reverse('add-team-member', args=[self.project.id])
        
        # Create another user for team member tests
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpassword'
        )
        
    def test_project_list_view_authenticated(self):
        """Test that authenticated users can access the project list view."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.project_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_list.html')
        self.assertContains(response, 'Test Project')
        
    def test_project_list_view_unauthenticated(self):
        """Test that unauthenticated users are redirected from the project list view."""
        response = self.client.get(self.project_list_url)
        self.assertRedirects(response, f'/login/?next={self.project_list_url}')
        
    def test_project_detail_view_authenticated_team_member(self):
        """Test that team members can access the project detail view."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.project_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_detail.html')
        self.assertContains(response, 'Test Project')
        
    def test_project_detail_view_authenticated_non_team_member(self):
        """Test that non-team members cannot access the project detail view."""
        self.client.login(username='testuser2', password='testpassword')
        response = self.client.get(self.project_detail_url)
        # Should redirect with an error message
        self.assertEqual(response.status_code, 302)
        
    def test_project_create_view_get(self):
        """Test that the project create view works correctly for GET requests."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.project_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_form.html')
        
    def test_project_create_view_post_valid(self):
        """Test that the project create view works correctly for valid POST requests."""
        self.client.login(username='testuser', password='testpassword')
        form_data = {
            'name': 'New Project',
            'description': 'This is a new project',
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() + timedelta(days=30),
            'is_active': True,
        }
        response = self.client.post(self.project_create_url, form_data)
        
        # Get the new project
        new_project = Project.objects.get(name='New Project')
        
        # Should redirect to the new project's detail page
        self.assertRedirects(response, reverse('project-detail', args=[new_project.id]))
        
        # Check that the project was created correctly
        self.assertEqual(new_project.description, 'This is a new project')
        self.assertEqual(new_project.created_by, self.user)
        self.assertIn(self.user, new_project.team_members.all())
        
        # Check that the user was assigned as owner
        project_role = ProjectRole.objects.get(user=self.user, project=new_project)
        self.assertEqual(project_role.role, 'OWNER')
        
    def test_add_team_member_view_get(self):
        """Test that the add team member view works correctly for GET requests."""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(self.add_team_member_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/add_team_member.html')
        
    def test_add_team_member_view_post_valid(self):
        """Test that the add team member view works correctly for valid POST requests."""
        self.client.login(username='testuser', password='testpassword')
        form_data = {
            'user': self.user2.id,
            'role': 'MEMBER',
        }
        response = self.client.post(self.add_team_member_url, form_data)
        
        # Should redirect to the project's detail page
        self.assertRedirects(response, self.project_detail_url)
        
        # Check that the user was added to the project
        self.project.refresh_from_db()
        self.assertIn(self.user2, self.project.team_members.all())
        
        # Check that the role was created correctly
        project_role = ProjectRole.objects.get(user=self.user2, project=self.project)
        self.assertEqual(project_role.role, 'MEMBER')
        
    def test_add_team_member_view_non_owner(self):
        """Test that non-owners cannot add team members."""
        # Create a new project where user2 is a member, not an owner
        project2 = Project.objects.create(
            name='Test Project 2',
            description='This is another test project',
            start_date=timezone.now().date(),
            created_by=self.user
        )
        project2.team_members.add(self.user, self.user2)
        ProjectRole.objects.create(user=self.user, project=project2, role='OWNER')
        ProjectRole.objects.create(user=self.user2, project=project2, role='MEMBER')
        
        # Try to add a team member as user2 (who is not an owner)
        self.client.login(username='testuser2', password='testpassword')
        add_url = reverse('add-team-member', args=[project2.id])
        response = self.client.get(add_url)
        
        # Should redirect with an error message
        self.assertEqual(response.status_code, 302)