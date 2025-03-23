import django_filters
from django import forms
from .models import Lesson, Category
from django.contrib.auth.models import User
from projects.models import Project

class LessonFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(
        lookup_expr='icontains',
        widget=forms.TextInput(attrs={'placeholder': 'Search lessons...'})
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
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    date_to = django_filters.DateFilter(
        field_name='date_identified',
        lookup_expr='lte',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    is_starred = django_filters.BooleanFilter(
        field_name='starred_by',
        method='filter_starred',
        widget=forms.CheckboxInput()
    )
    
    def filter_starred(self, queryset, name, value):
        if value and self.request and self.request.user:
            return queryset.filter(starred_by=self.request.user)
        return queryset
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = kwargs.get('request')
        
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