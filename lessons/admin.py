from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Category, Lesson, Attachment, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'lesson_count')
    search_fields = ('name',)
    
    def lesson_count(self, obj):
        return obj.lesson_set.count()
    
    lesson_count.short_description = 'Lessons'

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_date',)

@admin.register(Lesson)
class LessonAdmin(SummernoteModelAdmin):
    summernote_fields = ('description', 'recommendations', 'implementation_notes')
    list_display = ('title', 'project', 'category', 'date_identified', 'status', 'impact', 'submitted_by')
    list_filter = ('status', 'impact', 'category', 'project')
    search_fields = ('title', 'description', 'recommendations')
    date_hierarchy = 'date_identified'
    filter_horizontal = ('tags', 'starred_by')
    inlines = [AttachmentInline, CommentInline]
    readonly_fields = ('created_date', 'modified_date')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'project', 'category', 'date_identified')
        }),
        ('Content', {
            'fields': ('description', 'recommendations', 'implementation_notes')
        }),
        ('Status & Impact', {
            'fields': ('status', 'impact')
        }),
        ('Attribution', {
            'fields': ('submitted_by', 'tags', 'starred_by')
        }),
        ('Metadata', {
            'fields': ('created_date', 'modified_date'),
            'classes': ('collapse',)
        }),
    )