# lessons/management/commands/generate_test_data.py

import os
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from projects.models import Project, ProjectRole
from lessons.models import Category, Lesson, Attachment, Comment
from accounts.models import Profile


def create_test_users(count=10):
    """Create test users with profiles"""
    users = []
    departments = ['Engineering', 'Marketing', 'Sales', 'Operations', 'Finance', 'HR', 'IT', 'Product']
    job_titles = [
        'Manager', 'Director', 'Coordinator', 'Specialist', 'Analyst', 
        'Developer', 'Designer', 'Consultant', 'Assistant', 'Lead'
    ]
    
    print(f"Creating {count} test users...")
    
    for i in range(1, count + 1):
        username = f'testuser{i}'
        
        # Skip if user already exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            users.append(user)
            continue
            
        user = User.objects.create_user(
            username=username,
            email=f'user{i}@example.com',
            password='password123',
            first_name=f'Test{i}',
            last_name=f'User{i}'
        )
        
        # Manually create profile if it doesn't exist
        # This is the fix - check if profile exists and create it if needed
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            profile = Profile.objects.create(user=user)
        
        # Update profile
        profile.job_title = f'{random.choice(job_titles)}'
        profile.department = random.choice(departments)
        profile.save()
        
        users.append(user)
        
    print(f"Created {len(users)} users")
    return users


def create_test_projects(count=5, users=None):
    """Create test projects with team members"""
    if users is None or len(users) == 0:
        users = create_test_users()
        
    projects = []
    project_types = ['Development', 'Research', 'Marketing', 'Infrastructure', 'Implementation', 'Rollout']
    clients = ['Internal', 'Acme Corp', 'Globex', 'Initech', 'Umbrella', 'Stark Industries', 'Wayne Enterprises']
    
    print(f"Creating {count} test projects...")
    
    for i in range(1, count + 1):
        project_type = random.choice(project_types)
        client = random.choice(clients)
        
        # Randomize dates
        start_offset = random.randint(-180, -30)  # Between 6 months and 1 month ago
        start_date = timezone.now().date() + timedelta(days=start_offset)
        
        # 75% chance to set an end date
        has_end_date = random.random() < 0.75
        end_offset = random.randint(30, 180)  # Between 1 and 6 months from now
        end_date = timezone.now().date() + timedelta(days=end_offset) if has_end_date else None
        
        # 80% chance to be active
        is_active = random.random() < 0.8
        
        # Random creator from users
        creator = random.choice(users)
        
        project = Project.objects.create(
            name=f'{client} {project_type} Project {i}',
            description=f'This is a test project for {client} focusing on {project_type.lower()}. '
                       f'The project aims to deliver improved {project_type.lower()} capabilities '
                       f'and enhance operational efficiency.',
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
            created_by=creator
        )
        
        # Add creator as owner
        ProjectRole.objects.create(
            user=creator,
            project=project,
            role='OWNER'
        )
        project.team_members.add(creator)
        
        # Add random team members (between 1 and 5 additional members)
        team_size = random.randint(1, min(5, len(users) - 1))
        potential_members = [user for user in users if user != creator]
        
        if potential_members:
            team_members = random.sample(potential_members, min(team_size, len(potential_members)))
            
            for member in team_members:
                role = random.choice(['MANAGER', 'MEMBER', 'VIEWER'])
                ProjectRole.objects.create(
                    user=member,
                    project=project,
                    role=role
                )
                project.team_members.add(member)
        
        projects.append(project)
    
    print(f"Created {len(projects)} projects")
    return projects


def create_test_categories():
    """Create common lesson categories"""
    categories = []
    category_data = [
        ('Technical', 'Technical aspects of the project including code, architecture, and infrastructure.'),
        ('Process', 'Project management processes, methodologies, and workflows.'),
        ('Communication', 'Internal and external communication strategies and challenges.'),
        ('Team Dynamics', 'Team collaboration, management, and interpersonal dynamics.'),
        ('Client Relationship', 'Client interactions, expectation management, and satisfaction.'),
        ('Planning', 'Project planning, scheduling, and resource allocation.'),
        ('Quality', 'Quality assurance, testing, and standards compliance.'),
        ('Risk Management', 'Identification and mitigation of project risks.'),
    ]
    
    print("Creating lesson categories...")
    
    for name, description in category_data:
        category, created = Category.objects.get_or_create(
            name=name,
            defaults={'description': description}
        )
        categories.append(category)
    
    print(f"Created {len(categories)} categories")
    return categories


def create_test_lessons(count=20, projects=None, users=None, categories=None):
    """Create test lessons for projects"""
    if projects is None or len(projects) == 0:
        projects = create_test_projects()
        
    if categories is None or len(categories) == 0:
        categories = create_test_categories()
    
    all_users = []
    for project in projects:
        all_users.extend(project.team_members.all())
    all_users = list(set(all_users))
    
    if not all_users:
        all_users = create_test_users()
    
    lessons = []
    lesson_titles = [
        'Improve {0} methodology for better {1}',
        'Consider alternative approach to {0} for {1}',
        'Standardize {0} process across {1}',
        'Implement early {0} testing to prevent {1}',
        'Document {0} requirements earlier to avoid {1}',
        'Enhance {0} training to improve {1}',
        'Streamline {0} workflow to reduce {1}',
        'Allocate more resources to {0} to prevent {1}',
        'Redesign {0} process to eliminate {1}',
        'Clarify {0} expectations to minimize {1}'
    ]
    
    lesson_subjects = [
        'deployment', 'documentation', 'design', 'testing', 'communication',
        'planning', 'estimation', 'integration', 'resource allocation', 'risk assessment'
    ]
    
    lesson_outcomes = [
        'delays', 'misunderstandings', 'quality issues', 'scope creep', 'rework',
        'budget overruns', 'technical debt', 'stakeholder confusion', 'team friction', 'bottlenecks'
    ]
    
    statuses = ['NEW', 'ACKNOWLEDGED', 'IN_PROGRESS', 'IMPLEMENTED', 'ARCHIVED']
    impacts = ['HIGH', 'MEDIUM', 'LOW']
    
    print(f"Creating {count} test lessons...")
    
    for i in range(1, count + 1):
        project = random.choice(projects)
        
        # Get users from this project
        project_users = list(project.team_members.all())
        submitter = random.choice(project_users)
        
        # Random dates
        date_offset = random.randint(-90, -1)  # In the past 90 days
        date_identified = timezone.now().date() + timedelta(days=date_offset)
        
        # Generate title
        title_template = random.choice(lesson_titles)
        subject = random.choice(lesson_subjects)
        outcome = random.choice(lesson_outcomes)
        title = title_template.format(subject, outcome)
        
        # Generate content
        description = f"""<h3>Context</h3>
<p>During the {subject} phase of the project, we encountered issues with {outcome} that impacted our delivery timeline.</p>

<h3>Situation</h3>
<p>The team faced challenges when implementing the {subject} process because of insufficient planning and unclear requirements.</p>
<ul>
    <li>Initial approach was too complex</li>
    <li>Team members had varying levels of expertise in {subject}</li>
    <li>External dependencies were not adequately identified</li>
</ul>

<p>This resulted in {outcome} that required additional effort to resolve and delayed the project by approximately {random.randint(1, 10)} days.</p>"""

        recommendations = f"""<h3>Recommendations</h3>
<p>Based on our experience, we recommend the following changes for future projects:</p>

<ol>
    <li><strong>Improve planning:</strong> Dedicate more time to {subject} planning before implementation begins</li>
    <li><strong>Enhance documentation:</strong> Create clearer documentation with specific examples</li>
    <li><strong>Training:</strong> Ensure all team members have the necessary skills and knowledge</li>
    <li><strong>Regular reviews:</strong> Implement checkpoints to identify issues early</li>
</ol>

<p>By implementing these recommendations, we can minimize {outcome} in future projects and improve overall delivery efficiency.</p>"""

        implementation_notes = ""
        if random.random() < 0.3:  # 30% chance to have implementation notes
            implementation_notes = f"""<h3>Implementation Progress</h3>
<p>We have started implementing the recommended changes:</p>

<ul>
    <li>Created new {subject} templates for the team</li>
    <li>Updated the project methodology documentation</li>
    <li>Scheduled training sessions for team members</li>
</ul>

<p>Initial results are promising, with a {random.randint(10, 50)}% reduction in {outcome} observed in the latest sprint.</p>"""

        # Create the lesson
        lesson = Lesson.objects.create(
            project=project,
            date_identified=date_identified,
            category=random.choice(categories),
            title=title,
            description=description,
            recommendations=recommendations,
            impact=random.choice(impacts),
            status=random.choice(statuses),
            implementation_notes=implementation_notes,
            submitted_by=submitter
        )
        
        # Maybe add tags (50% chance)
        if random.random() < 0.5:
            tag_count = random.randint(1, min(3, len(project_users)))
            tags = random.sample(project_users, tag_count)
            lesson.tags.set(tags)
        
        # Maybe add stars (30% chance)
        if random.random() < 0.3:
            star_count = random.randint(1, min(3, len(project_users)))
            stars = random.sample(project_users, star_count)
            lesson.starred_by.set(stars)
        
        lessons.append(lesson)
    
    print(f"Created {len(lessons)} lessons")
    return lessons


def create_test_comments(lessons=None, min_comments=0, max_comments=5):
    """Add random comments to lessons"""
    if lessons is None or len(lessons) == 0:
        print("No lessons provided for creating comments")
        return []
    
    comments = []
    comment_templates = [
        "Great point! We should definitely follow this recommendation on future projects.",
        "I had a similar experience on the {0} project. We solved it by implementing more rigorous testing.",
        "This is an important lesson. I wonder if we could automate some of these processes to prevent this issue.",
        "I agree with the recommendation, but I think we should also consider {0} as a potential solution.",
        "Has anyone tried implementing this in their recent projects? I'd like to know how effective it was.",
        "This resonates with me. We faced similar challenges and found that early stakeholder involvement helped.",
        "Good lesson. I'd add that documentation played a key role in our ability to address similar issues.",
        "I think we need to share this more widely across the organization.",
        "Good insight. Would it be worth creating a training module about this for new team members?",
        "I've shared this with my team - very relevant to our current work."
    ]
    
    topics = [
        "Alpha", "Beta", "Gamma", "Delta", "cloud migration", "system integration",
        "agile transformation", "DevOps", "user testing", "requirements gathering"
    ]
    
    print("Creating test comments...")
    comment_count = 0
    
    for lesson in lessons:
        # Get users who have access to this lesson's project
        available_commenters = list(lesson.project.team_members.all())
        
        # Random number of comments for this lesson
        num_comments = random.randint(min_comments, max_comments)
        
        for _ in range(num_comments):
            # Don't let the submitter comment on their own lesson all the time
            if random.random() < 0.7:  # 70% chance to have someone else comment
                potential_commenters = [u for u in available_commenters if u != lesson.submitted_by]
                if potential_commenters:
                    commenter = random.choice(potential_commenters)
                else:
                    commenter = lesson.submitted_by
            else:
                commenter = lesson.submitted_by
            
            # Generate comment text from template
            template = random.choice(comment_templates)
            topic = random.choice(topics)
            comment_text = template.format(topic)
            
            # Create comment
            comment = Comment.objects.create(
                lesson=lesson,
                author=commenter,
                text=comment_text,
                created_date=timezone.now() - timedelta(days=random.randint(0, 30), 
                                                       hours=random.randint(0, 23),
                                                       minutes=random.randint(0, 59))
            )
            
            comments.append(comment)
            comment_count += 1
    
    print(f"Created {comment_count} comments")
    return comments


def create_test_attachments(lessons=None, attachment_probability=0.3):
    """Add random attachments to lessons"""
    if lessons is None or len(lessons) == 0:
        print("No lessons provided for creating attachments")
        return []
    
    attachments = []
    attachment_count = 0
    
    # Ensure the media directory exists
    media_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'media', 'lesson_attachments')
    os.makedirs(media_dir, exist_ok=True)
    
    # Sample text for TXT files
    sample_text = """This is a sample document for testing attachments in the Lessons Learned System.
It contains some placeholder text for demonstration purposes.

The attachment functionality allows users to add supporting documentation to their lessons,
which helps provide context and additional information for future reference.

This feature is particularly useful for:
- Sharing detailed technical specifications
- Including relevant diagrams or charts
- Providing templates for future projects
- Documenting specific procedures or workflows

Testing the attachment functionality is an important part of ensuring
the Lessons Learned System works correctly and provides value to users."""

    print("Creating test attachments...")
    
    for lesson in lessons:
        # Each lesson has a 30% chance (or specified probability) of having an attachment
        if random.random() < attachment_probability:
            submitter = lesson.submitted_by
            
            # Create a simple text file as an attachment
            file_name = f"attachment_for_lesson_{lesson.id}.txt"
            
            # Create a temporary file
            file_content = sample_text.encode('utf-8')
            temp_file = SimpleUploadedFile(file_name, file_content, content_type='text/plain')
            
            # Create the attachment
            description = random.choice([
                "Supporting documentation",
                "Process diagram",
                "Meeting notes",
                "Reference material",
                "Implementation guide",
                "Technical specifications",
                ""  # Empty description sometimes
            ])
            
            attachment = Attachment.objects.create(
                lesson=lesson,
                file=temp_file,
                uploaded_by=submitter,
                description=description
            )
            
            attachments.append(attachment)
            attachment_count += 1
    
    print(f"Created {attachment_count} attachments")
    return attachments


class Command(BaseCommand):
    help = 'Creates test data for the Lessons Learned System'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of test users to create')
        parser.add_argument('--projects', type=int, default=5, help='Number of test projects to create')
        parser.add_argument('--lessons', type=int, default=20, help='Number of test lessons to create')
        parser.add_argument('--min-comments', type=int, default=0, help='Minimum comments per lesson')
        parser.add_argument('--max-comments', type=int, default=5, help='Maximum comments per lesson')
        parser.add_argument('--attachment-probability', type=float, default=0.3, 
                           help='Probability (0-1) of a lesson having an attachment')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting test data generation...'))
        
        # Create test data in the right order
        users = create_test_users(options['users'])
        categories = create_test_categories()
        projects = create_test_projects(options['projects'], users)
        lessons = create_test_lessons(options['lessons'], projects, users, categories)
        create_test_comments(lessons, options['min_comments'], options['max_comments'])
        create_test_attachments(lessons, options['attachment_probability'])
        
        self.stdout.write(self.style.SUCCESS('Test data generation complete!'))