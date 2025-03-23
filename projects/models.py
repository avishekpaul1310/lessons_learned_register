from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    team_members = models.ManyToManyField(User, related_name='projects')
    
    def __str__(self):
        return self.name

class ProjectRole(models.Model):
    ROLE_CHOICES = [
        ('OWNER', 'Project Owner'),
        ('MANAGER', 'Project Manager'),
        ('MEMBER', 'Team Member'),
        ('VIEWER', 'Viewer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='MEMBER')
    
    class Meta:
        unique_together = ('user', 'project')
        
    def __str__(self):
        return f'{self.user.username} - {self.project.name} - {self.role}'