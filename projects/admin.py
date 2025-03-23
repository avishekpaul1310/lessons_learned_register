from django.contrib import admin
from .models import Project, ProjectRole

class ProjectRoleInline(admin.TabularInline):
    model = ProjectRole
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active', 'created_by', 'team_count')
    list_filter = ('is_active', 'start_date')
    search_fields = ('name', 'description')
    date_hierarchy = 'start_date'
    inlines = [ProjectRoleInline]
    
    def team_count(self, obj):
        return obj.team_members.count()
    
    team_count.short_description = 'Team Members'