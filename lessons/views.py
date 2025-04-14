from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator
from .models import Lesson, Category, Attachment, Comment
from .forms import LessonForm, AttachmentForm, CommentForm
from projects.models import Project
from django_filters.views import FilterView
from .filters import LessonFilter
import csv
from django.template.loader import render_to_string
# Comment out WeasyPrint to avoid dependency issues on Windows
# from weasyprint import HTML
import tempfile
from django.db.models import Count, Q

@login_required
def lesson_list(request):
    # Get all lessons from user's projects with optimized query
    user_projects = request.user.projects.all()
    lessons = Lesson.objects.filter(project__in=user_projects).select_related(
        'project', 'category', 'submitted_by'
    )
    
    # Apply filters
    lesson_filter = LessonFilter(request.GET, queryset=lessons, request=request)
    
    # Handle export
    if 'export' in request.GET:
        export_format = request.GET.get('export')
        filtered_lessons = lesson_filter.qs
        
        if export_format == 'csv':
            return export_lessons_csv(filtered_lessons)
        elif export_format == 'pdf':
            return export_lessons_pdf(filtered_lessons)
    
    # Pagination
    paginator = Paginator(lesson_filter.qs.order_by('-created_date'), 12)  # Show 12 lessons per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'filter': lesson_filter,
        'page_obj': page_obj,
    }
    
    return render(request, 'lessons/lesson_list.html', context)

@login_required
def lesson_detail(request, pk):
    lesson = get_object_or_404(
        Lesson.objects.select_related('project', 'category', 'submitted_by'), 
        pk=pk
    )
    
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
        'comments': lesson.comments.select_related('author').order_by('-created_date'),
        'comment_form': comment_form,
        'is_starred': lesson.starred_by.filter(id=request.user.id).exists(),
        'attachments': lesson.attachments.select_related('uploaded_by'),
        'related_lessons': Lesson.objects.filter(
            project=lesson.project
        ).exclude(pk=lesson.pk).order_by('-created_date')[:3],
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
        # Pre-fill project if provided in GET parameters
        initial_data = {}
        if 'project' in request.GET:
            initial_data['project'] = request.GET.get('project')
            
        form = LessonForm(user=request.user, initial=initial_data)
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

@login_required
def delete_attachment(request, pk):
    attachment = get_object_or_404(Attachment, pk=pk)
    lesson_pk = attachment.lesson.pk
    
    # Check if user has permission to delete
    if attachment.uploaded_by != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to delete this attachment.")
        return redirect('lesson-detail', pk=lesson_pk)
    
    if request.method == 'POST':
        attachment.delete()
        messages.success(request, "Attachment has been deleted.")
        return redirect('lesson-detail', pk=lesson_pk)
    
    return render(request, 'lessons/confirm_delete.html', {
        'object': attachment,
        'cancel_url': f'/lessons/{lesson_pk}/'
    })

@login_required
def delete_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    
    # Check if user has permission to delete
    if lesson.submitted_by != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to delete this lesson.")
        return redirect('lesson-detail', pk=pk)
    
    if request.method == 'POST':
        project = lesson.project  # Store project before deletion for redirect
        lesson.delete()
        messages.success(request, "Lesson has been deleted.")
        return redirect('project-detail', pk=project.pk)
    
    return render(request, 'lessons/confirm_delete.html', {
        'object': lesson,
        'cancel_url': f'/lessons/{pk}/'
    })

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

# Alternative PDF export that doesn't use WeasyPrint
def export_lessons_pdf(queryset):
    """
    HTML-based alternative to WeasyPrint PDF export
    """
    html_string = render_to_string('lessons/pdf_template.html', {'lessons': queryset})
    
    response = HttpResponse(content_type='text/html')
    response['Content-Disposition'] = 'attachment; filename="lessons_learned.html"'
    
    # Add print script to automatically print when opened
    print_script = """
    <script>
        window.onload = function() {
            document.title = "Lessons Learned Report";
            setTimeout(function() {
                window.print();
            }, 500);
        }
    </script>
    """
    
    # Insert the script right before the closing </body> tag
    modified_html = html_string.replace('</body>', f'{print_script}</body>')
    
    response.write(modified_html)
    return response

@login_required
def dashboard(request):
    user_projects = request.user.projects.all()
    
    # Get latest lessons with optimized query
    latest_lessons = Lesson.objects.filter(project__in=user_projects).select_related(
        'project', 'category', 'submitted_by'
    ).order_by('-created_date')[:5]
    
    # Get starred lessons with optimized query
    starred_lessons = request.user.starred_lessons.select_related(
        'project', 'category', 'submitted_by'
    ).all()
    
    # Get lessons by category
    categories = Category.objects.filter(lesson__project__in=user_projects).distinct()
    lessons_by_category = {}
    
    category_counts = Lesson.objects.filter(
        project__in=user_projects
    ).values('category__name').annotate(count=Count('category')).order_by('-count')
    
    for item in category_counts:
        category_name = item['category__name'] or 'Uncategorized'
        lessons_by_category[category_name] = item['count']
    
    # Get lessons by status - more efficient query
    status_counts = Lesson.objects.filter(
        project__in=user_projects
    ).values('status').annotate(count=Count('status')).order_by('status')
    
    lessons_by_status = {}
    for item in status_counts:
        status_code = item['status']
        status_display = dict(Lesson.STATUS_CHOICES).get(status_code, status_code)
        lessons_by_status[status_display] = item['count']
    
    # Get high impact lessons count
    high_impact_count = Lesson.objects.filter(
        project__in=user_projects, 
        impact='HIGH'
    ).count()
    
    context = {
        'latest_lessons': latest_lessons,
        'starred_lessons': starred_lessons,
        'lessons_by_category': lessons_by_category,
        'lessons_by_status': lessons_by_status,
        'total_lessons': Lesson.objects.filter(project__in=user_projects).count(),
        'user_projects': user_projects,
        'high_impact_count': high_impact_count,
    }
    
    return render(request, 'lessons/dashboard.html', context)

@login_required
def create_category(request):
    """Create a new category via AJAX request"""
    if request.method == 'POST':
        category_name = request.POST.get('category_name', '').strip()
        if category_name:
            # Check if category already exists
            existing = Category.objects.filter(name__iexact=category_name).first()
            if existing:
                return HttpResponse(f'{{"id": {existing.id}, "name": "{existing.name}", "status": "exists"}}', 
                                    content_type='application/json')
            
            # Create new category
            category = Category.objects.create(name=category_name)
            return HttpResponse(f'{{"id": {category.id}, "name": "{category.name}", "status": "created"}}', 
                                content_type='application/json')
        
        return HttpResponse('{"error": "Category name is required"}', status=400, content_type='application/json')
    
    return HttpResponse('{"error": "Method not allowed"}', status=405, content_type='application/json')