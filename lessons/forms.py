from django import forms
from django.contrib.auth.models import User
from django_summernote.widgets import SummernoteWidget
from .models import Lesson, Attachment, Comment, Category
from projects.models import Project

class LessonForm(forms.ModelForm):
    tagged_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    
    # Define unique field names for the rich text editors to avoid duplicate IDs
    lesson_description = forms.CharField(
        required=True,
        widget=SummernoteWidget(attrs={'summernote': {'height': '200px'}}),
        label="Description"
    )
    
    lesson_recommendations = forms.CharField(
        required=True,
        widget=SummernoteWidget(attrs={'summernote': {'height': '200px'}}),
        label="Recommendations"
    )
    
    class Meta:
        model = Lesson
        fields = [
            'project', 'title', 'category', 'date_identified', 
            'impact', 'status', 'implementation_notes'
        ]
        widgets = {
            'date_identified': forms.DateInput(attrs={'type': 'date'}),
            'implementation_notes': SummernoteWidget(attrs={'summernote': {'height': '150px'}}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If we have an instance, initialize the custom fields with instance data
        if self.instance and self.instance.pk:
            self.fields['lesson_description'].initial = self.instance.description
            self.fields['lesson_recommendations'].initial = self.instance.recommendations
            # For existing lessons, keep their status
        else:
            # For new lessons, explicitly set the default status to NEW
            self.initial['status'] = 'NEW'
        
        # Limit projects to ones the user is part of
        if user:
            self.fields['project'].queryset = Project.objects.filter(team_members=user)
            
            # Get list of users from the same projects as the current user
            project_ids = user.projects.values_list('id', flat=True)
            self.fields['tagged_users'].queryset = User.objects.filter(
                projects__in=project_ids
            ).distinct().exclude(id=user.id)
            
            # If editing an existing lesson, include currently tagged users
            if self.instance.pk:
                self.initial['tagged_users'] = self.instance.tags.all()
        
        # Handle pre-selected project from URL parameters
        if 'initial' in kwargs and kwargs['initial'] and 'project' in kwargs['initial']:
            project_id = kwargs['initial']['project']
            try:
                self.fields['project'].initial = Project.objects.get(pk=project_id)
            except Project.DoesNotExist:
                pass
    
    def clean_lesson_description(self):
        """Validate description field"""
        description = self.cleaned_data.get('lesson_description', '')
        empty_patterns = ['', '<p></p>', '<p>&nbsp;</p>', '&nbsp;']
        
        if not description or description.strip() in empty_patterns:
            raise forms.ValidationError("Please provide a description.")
        return description
    
    def clean_lesson_recommendations(self):
        """Validate recommendations field"""
        recommendations = self.cleaned_data.get('lesson_recommendations', '')
        empty_patterns = ['', '<p></p>', '<p>&nbsp;</p>', '&nbsp;']
        
        if not recommendations or recommendations.strip() in empty_patterns:
            raise forms.ValidationError("Please provide recommendations.")
        return recommendations
    
    def save(self, commit=True):
        """Override save to handle the custom rich text fields"""
        lesson = super().save(commit=False)
        
        # Set the model fields from our custom form fields
        lesson.description = self.cleaned_data.get('lesson_description', '')
        lesson.recommendations = self.cleaned_data.get('lesson_recommendations', '')
        
        # For new lessons, make sure status is NEW if not otherwise specified
        if not lesson.pk and not lesson.status:
            lesson.status = 'NEW'
        
        if commit:
            lesson.save()
        
        return lesson

class AttachmentForm(forms.ModelForm):
    # Make file field optional for form display, but will validate in clean if submitted
    file = forms.FileField(required=False)
    
    class Meta:
        model = Attachment
        fields = ['file', 'description']
        
    def clean(self):
        cleaned_data = super().clean()
        # If the form was submitted with no file, return empty cleaned_data
        # This will cause the view to skip creating the attachment
        if not cleaned_data.get('file'):
            return {}
        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add your comment here...'}),
        }