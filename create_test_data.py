from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

from accounts.models import Profile
from projects.models import Project, ProjectRole
from lessons.models import Category, Lesson, Comment, Attachment

def fix_profile_model():
    """
    This is a monkey patch to avoid image resizing in the Profile model's save method.
    It replaces the save method temporarily.
    """
    old_save = Profile.save
    
    def new_save(self, *args, **kwargs):
        import django.db.models
        django.db.models.Model.save(self, *args, **kwargs)
    
    Profile.save = new_save
    
    return old_save

def restore_profile_model(old_save):
    """Restore the original save method"""
    Profile.save = old_save

def create_default_image():
    """Create a default profile image and return it as ContentFile"""
    # Create a simple image
    image_file = BytesIO()
    image = Image.new('RGB', (100, 100), color='gray')
    image.save(image_file, 'JPEG')
    image_file.seek(0)
    
    return ContentFile(image_file.read(), name='profile.jpg')

def create_test_data():
    print("Creating test data...")
    
    # Temporarily patch the profile model to avoid image resizing issue
    old_save = fix_profile_model()

    try:
        # Create test users
        print("Creating users...")
        users = []
        
        for i in range(1, 4):
            username = f"testuser{i}"
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
            else:
                user = User.objects.create_user(
                    username=username,
                    email=f"testuser{i}@example.com",
                    password="password123",
                    first_name=f"Test{i}",
                    last_name="User"
                )
                
                # Manually create profile
                if not hasattr(user, 'profile'):
                    profile = Profile(user=user)
                    profile.job_title = f"Job Title {i}"
                    profile.department = f"Department {i}"
                    profile.image = create_default_image()
                    profile.save()
            
            users.append(user)
        
        print(f"Created {len(users)} users")
        
        # Create categories
        print("Creating categories...")
        categories = []
        category_names = ["Technical", "Process", "Communication"]
        
        for name in category_names:
            category, created = Category.objects.get_or_create(name=name)
            categories.append(category)
        
        print(f"Created {len(categories)} categories")
        
        # Create projects
        print("Creating projects...")
        projects = []
        
        for i in range(1, 3):
            name = f"Test Project {i}"
            if Project.objects.filter(name=name).exists():
                project = Project.objects.get(name=name)
            else:
                project = Project.objects.create(
                    name=name,
                    description=f"Description for project {i}",
                    start_date=timezone.now().date(),
                    is_active=True,
                    created_by=users[0]
                )
                
                # Add team members
                project.team_members.add(*users)
                
                # Create roles
                ProjectRole.objects.get_or_create(user=users[0], project=project, defaults={'role': 'OWNER'})
                ProjectRole.objects.get_or_create(user=users[1], project=project, defaults={'role': 'MANAGER'})
                ProjectRole.objects.get_or_create(user=users[2], project=project, defaults={'role': 'MEMBER'})
            
            projects.append(project)
        
        print(f"Created {len(projects)} projects")
        
        # Create lessons
        print("Creating lessons...")
        lessons = []
        statuses = ['NEW', 'ACKNOWLEDGED', 'IN_PROGRESS', 'IMPLEMENTED']
        impacts = ['HIGH', 'MEDIUM', 'LOW']
        
        for i in range(6):
            project = projects[min(i % len(projects), len(projects)-1)]
            category = categories[min(i % len(categories), len(categories)-1)]
            user = users[min(i % len(users), len(users)-1)]
            
            title = f"Test Lesson {i+1}"
            if Lesson.objects.filter(title=title, project=project).exists():
                lesson = Lesson.objects.get(title=title, project=project)
            else:
                lesson = Lesson.objects.create(
                    project=project,
                    title=title,
                    category=category,
                    date_identified=timezone.now().date() - timedelta(days=i),
                    description=f"<p>Test description for lesson {i+1}</p>",
                    recommendations=f"<p>Test recommendations for lesson {i+1}</p>",
                    impact=impacts[min(i % len(impacts), len(impacts)-1)],
                    status=statuses[min(i % len(statuses), len(statuses)-1)],
                    submitted_by=user
                )
                
                # Add tags and stars
                if i % 2 == 0:
                    lesson.tags.add(users[min((i+1) % len(users), len(users)-1)])
                
                if i % 3 == 0:
                    lesson.starred_by.add(users[min((i+2) % len(users), len(users)-1)])
            
            lessons.append(lesson)
        
        print(f"Created {len(lessons)} lessons")
        
        # Create comments
        print("Creating comments...")
        comment_count = 0
        
        for i, lesson in enumerate(lessons):
            # Only add comments if there are none
            if not Comment.objects.filter(lesson=lesson).exists():
                for j in range(2):
                    user = users[min((i+j) % len(users), len(users)-1)]
                    Comment.objects.create(
                        lesson=lesson,
                        author=user,
                        text=f"Test comment {j+1} for lesson {i+1}",
                        created_date=timezone.now() - timedelta(days=j, hours=j)
                    )
                    comment_count += 1
        
        print(f"Created {comment_count} comments")
        
        print("Test data creation completed successfully!")

    finally:
        # Restore the original save method
        restore_profile_model(old_save)

# Execute the function
create_test_data()