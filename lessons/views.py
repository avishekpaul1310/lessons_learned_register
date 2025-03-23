from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Lesson, Category, Attachment, Comment
from .forms import LessonForm, AttachmentForm, CommentForm
from projects.models import Project
from django_filters.views import FilterView
from .filters import LessonFilter
import csv
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile

@login_required
def lesson_list(request):
    # Get all lessons from user's projects
    user_projects = request.user.projects.all()
    lessons = Lesson.objects.filter(project__in=user_projects).select_related('project', 'category', 'submitted_by')
    
    # Apply filters
    lesson_filter = LessonFilter(request.GET, queryset=lessons)
    
    # Handle export
    if 'export' in request.GET:
        export_format = request.GET.get('export')
        filtered_lessons = lesson_filter.qs
        
        if export_format == 'csv':
            return export_lessons_csv(filtered_lessons)
        elif export_format == 'pdf':
            return export_lessons_pdf(filtered_lessons)
    
    context = {
        'filter': lesson_filter,
    }
    
    return render(request, 'lessons/lesson_list.html', context)

@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    
    # Check if user has access to this lesson's project
    if request.user not in lesson.project.team_members.all():
        messages.error(request, "You don't have access to this lesson.")
        return redirect('lesson-list')
    
    # Handle comment form
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.lesson = lesson
            comment.author = request.user
            comment.save()
            messages.success(request, "Your comment has been added.")
            return redirect('lesson-detail', pk=lesson.pk)
    else:
        comment_form = CommentForm()
    
    # Handle star/unstar
    if 'star' in request.GET:
        if lesson.starred_by.filter(id=request.user.id).exists():
            lesson.starred_by.remove(request.user)
            messages.info(request, "Lesson removed from your starred items.")
        else:
            lesson.starred_by.add(request.user)
            messages.success(request, "Lesson added to your starred items.")
        return redirect('lesson-detail', pk=lesson.pk)
    
    context = {
        'lesson': lesson,
        'comments': lesson.comments.all().order_by('-created_date'),
        'comment_form': comment_form,
        'is_starred': lesson.starred_by.filter(id=request.user.id).exists(),
        'attachments': lesson.attachments.all(),
    }
    
    return render(request, 'lessons/lesson_detail.html', context)

@login_required
def lesson_create(request):
    if request.method == 'POST':
        form = LessonForm(request.POST, user=request.user)
        attachment_form = AttachmentForm(request.POST, request.FILES)
        
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.submitted_by = request.user
            lesson.save()
            
            # Handle tagged users
            if form.cleaned_data.get('tagged_users'):
                lesson.tags.set(form.cleaned_data['tagged_users'])
            
            # Handle attachments
            if attachment_form.is_valid() and request.FILES:
                attachment = attachment_form.save(commit=False)
                attachment.lesson = lesson
                attachment.uploaded_by = request.user
                attachment.save()
            
            messages.success(request, "Lesson has been created successfully!")
            return redirect('lesson-detail', pk=lesson.pk)
    else:
        form = LessonForm(user=request.user)
        attachment_form = AttachmentForm()
    
    context = {
        'form': form,
        'attachment_form': attachment_form,
    }
    
    return render(request, 'lessons/lesson_form.html', context)

@login_required
def lesson_update(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    
    # Check if user has permission to edit
    if lesson.submitted_by != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to edit this lesson.")
        return redirect('lesson-detail', pk=lesson.pk)
    
    if request.method == 'POST':
        form = LessonForm(request.POST, instance=lesson, user=request.user)
        attachment_form = AttachmentForm(request.POST, request.FILES)
        
        if form.is_valid():
            lesson = form.save()
            
            # Handle tagged users
            if form.cleaned_data.get('tagged_users'):
                lesson.tags.set(form.cleaned_data['tagged_users'])
            
            # Handle attachments
            if attachment_form.is_valid() and request.FILES:
                attachment = attachment_form.save(commit=False)
                attachment.lesson = lesson
                attachment.uploaded_by = request.user
                attachment.save()
            
            messages.success(request, "Lesson has been updated successfully!")
            return redirect('lesson-detail', pk=lesson.pk)
    else:
        form = LessonForm(instance=lesson, user=request.user)
        attachment_form = AttachmentForm()
    
    context = {
        'form': form,
        'attachment_form': attachment_form,
        'lesson': lesson,
    }
    
    return render(request, 'lessons/lesson_form.html', context)

def export_lessons_csv(queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="lessons_learned.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Project', 'Title', 'Category', 'Date Identified', 'Status', 'Impact', 'Description', 'Recommendations', 'Submitted By'])
    
    for lesson in queryset:
        writer.writerow([
            lesson.project.name,
            lesson.title,
            lesson.category.name if lesson.category else '',
            lesson.date_identified,
            lesson.get_status_display(),
            lesson.get_impact_display(),
            lesson.description,
            lesson.recommendations,
            lesson.submitted_by.username,
        ])
    
    return response

def export_lessons_pdf(queryset):
    html_string = render_to_string('lessons/pdf_template.html', {'lessons': queryset})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="lessons_learned.pdf"'
    
    # Generate PDF
    HTML(string=html_string).write_pdf(response)
    
    return response

@login_required
def dashboard(request):
    user_projects = request.user.projects.all()
    
    # Get latest lessons
    latest_lessons = Lesson.objects.filter(project__in=user_projects).order_by('-created_date')[:5]
    
    # Get starred lessons
    starred_lessons = request.user.starred_lessons.all()
    
    # Get lessons by category
    categories = Category.objects.filter(lesson__project__in=user_projects).distinct()
    lessons_by_category = {}
    for category in categories:
        lessons_by_category[category.name] = Lesson.objects.filter(
            category=category, 
            project__in=user_projects
        ).count()
    
    # Get lessons by status
    lessons_by_status = {}
    for status, _ in Lesson.STATUS_CHOICES:
        lessons_by_status[status] = Lesson.objects.filter(
            status=status, 
            project__in=user_projects
        ).count()
    
    context = {
        'latest_lessons': latest_lessons,
        'starred_lessons': starred_lessons,
        'lessons_by_category': lessons_by_category,
        'lessons_by_status': lessons_by_status,
        'total_lessons': Lesson.objects.filter(project__in=user_projects).count(),
        'user_projects': user_projects,
    }
    
    return render(request, 'lessons/dashboard.html', context)