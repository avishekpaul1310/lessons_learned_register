from django import forms
from django.contrib.auth.models import User
from .models import Project, ProjectRole

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ProjectRoleForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by('username'),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    role = forms.ChoiceField(
        choices=ProjectRole.ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )