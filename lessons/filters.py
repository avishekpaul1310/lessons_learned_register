import django_filters
from django import forms
from .models import Lesson, Category
from django.contrib.auth.models import User
from projects.models import Project

class LessonFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Search lessons...', 'class': 'form-control'})
    )
    
    project = django_filters.ModelChoiceFilter(
        queryset=Project.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = django_filters.ChoiceFilter(
        choices=Lesson.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    impact = django_filters.ChoiceFilter(
        choices=Lesson.IMPACT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    submitted_by = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = django_filters.DateFilter(
        field_name='date_identified',
        lookup_expr='gte',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    date_to = django_filters.DateFilter(
        field_name='date_identified',
        lookup_expr='lte',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    is_starred = django_filters.BooleanFilter(
        field_name='starred_by',
        method='filter_starred',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def filter_starred(self, queryset, name, value):
        """Filter lessons by whether they are starred by the current user."""
    # Only apply the filter if value is True (checkbox is checked)
        if value:
        # Make sure we have a valid request and user
            if hasattr(self, 'request') and self.request and hasattr(self.request, 'user') and self.request.user.is_authenticated:
            # Return only lessons where the current user is in the starred_by relationship
                return queryset.filter(starred_by=self.request.user)
    # Otherwise, return unfiltered queryset
        return queryset
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # If user is logged in, filter projects by user's projects
        if self.request and self.request.user.is_authenticated:
            self.filters['project'].queryset = Project.objects.filter(
                team_members=self.request.user
            )
            self.filters['submitted_by'].queryset = User.objects.filter(
                projects__team_members=self.request.user
            ).distinct()
    
    class Meta:
        model = Lesson
        fields = [
            'title', 'project', 'category', 'status', 
            'impact', 'submitted_by', 'date_from', 'date_to'
        ]