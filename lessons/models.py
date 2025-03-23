from django.db import models
from django.contrib.auth.models import User
from projects.models import Project

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
        
    def __str__(self):
        return self.name

class Lesson(models.Model):
    IMPACT_CHOICES = [
        ('HIGH', 'High'),
        ('MEDIUM', 'Medium'),
        ('LOW', 'Low'),
    ]
    
    STATUS_CHOICES = [
        ('NEW', 'New'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('IN_PROGRESS', 'In Progress'),
        ('IMPLEMENTED', 'Implemented'),
        ('ARCHIVED', 'Archived'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='lessons')
    date_identified = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    recommendations = models.TextField()
    impact = models.CharField(max_length=10, choices=IMPACT_CHOICES, default='MEDIUM')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='NEW')
    implementation_notes = models.TextField(blank=True)
    
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submitted_lessons')
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    
    tags = models.ManyToManyField(User, related_name='tagged_lessons', blank=True)
    starred_by = models.ManyToManyField(User, related_name='starred_lessons', blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.project.name})"

class Attachment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='lesson_attachments')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=255, blank=True)
    
    def __str__(self):
        return f"Attachment for {self.lesson.title}"

class Comment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.lesson.title}"