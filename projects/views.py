from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project, ProjectRole
from .forms import ProjectForm, ProjectRoleForm
from django.db.models import Count, Q

@login_required
def project_list(request):
    user_projects = Project.objects.filter(team_members=request.user)
    context = {
        'projects': user_projects
    }
    return render(request, 'projects/project_list.html', context)

@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has access to this project
    if request.user not in project.team_members.all():
        messages.error(request, "You don't have access to this project.")
        return redirect('project-list')
    
    # Get project role
    try:
        user_role = ProjectRole.objects.get(user=request.user, project=project).role
    except ProjectRole.DoesNotExist:
        user_role = None
    
    # Get project statistics
    lesson_stats = {
        'total': project.lessons.count(),
        'implemented': project.lessons.filter(status='IMPLEMENTED').count(),
        'high_impact': project.lessons.filter(impact='HIGH').count(),
    }
    
    # Get category distribution for chart
    category_counts = project.lessons.values('category__name').annotate(count=Count('category')).order_by('-count')
    categories_data = {}
    for item in category_counts:
        category_name = item['category__name'] or 'Uncategorized'
        categories_data[category_name] = item['count']
    
    # Get status distribution for chart
    status_counts = project.lessons.values('status').annotate(count=Count('status')).order_by('status')
    status_data = {}
    for item in status_counts:
        status_code = item['status']
        from lessons.models import Lesson
        status_display = dict(Lesson.STATUS_CHOICES).get(status_code, status_code)
        status_data[status_display] = item['count']
    
    # Convert to JSON for JS charts
    import json
    category_labels = list(categories_data.keys())
    category_values = list(categories_data.values())
    status_labels = list(status_data.keys())
    status_values = list(status_data.values())
    
    context = {
        'project': project,
        'user_role': user_role,
        'lesson_stats': lesson_stats,
        'team_members': ProjectRole.objects.filter(project=project).select_related('user'),
        'category_labels_json': json.dumps(category_labels),
        'category_values_json': json.dumps(category_values),
        'status_labels_json': json.dumps(status_labels),
        'status_values_json': json.dumps(status_values),
        'has_category_data': len(category_labels) > 0,
        'has_status_data': len(status_labels) > 0,
    }
    
    return render(request, 'projects/project_detail.html', context)

@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()
            
            # Add creator as project owner
            ProjectRole.objects.create(
                user=request.user,
                project=project,
                role='OWNER'
            )
            
            # Add creator to team members
            project.team_members.add(request.user)
            
            messages.success(request, f'Project "{project.name}" has been created!')
            return redirect('project-detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'projects/project_form.html', {'form': form})

@login_required
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has permission to edit project
    try:
        user_role = ProjectRole.objects.get(user=request.user, project=project).role
        if user_role not in ['OWNER', 'MANAGER']:
            messages.error(request, "You don't have permission to edit this project.")
            return redirect('project-detail', pk=project.pk)
    except ProjectRole.DoesNotExist:
        messages.error(request, "You don't have permission to edit this project.")
        return redirect('project-detail', pk=project.pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, f'Project "{project.name}" has been updated!')
            return redirect('project-detail', pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/project_form.html', {
        'form': form,
        'project': project
    })

@login_required
def add_team_member(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user has permission to add members
    try:
        user_role = ProjectRole.objects.get(user=request.user, project=project).role
        if user_role not in ['OWNER', 'MANAGER']:
            messages.error(request, "You don't have permission to add team members.")
            return redirect('project-detail', pk=project.pk)
    except ProjectRole.DoesNotExist:
        messages.error(request, "You don't have permission to add team members.")
        return redirect('project-detail', pk=project.pk)
    
    if request.method == 'POST':
        form = ProjectRoleForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            role = form.cleaned_data['role']
            
            # Check if user is already in the project
            if project.team_members.filter(id=user.id).exists():
                # Update role if already exists
                project_role = ProjectRole.objects.get(user=user, project=project)
                project_role.role = role
                project_role.save()
                messages.info(request, f'{user.username}\'s role has been updated to {role}.')
            else:
                # Add new team member
                ProjectRole.objects.create(user=user, project=project, role=role)
                project.team_members.add(user)
                messages.success(request, f'{user.username} has been added to the project as {role}.')
                
            return redirect('project-detail', pk=project.pk)
    else:
        form = ProjectRoleForm()
    
    return render(request, 'projects/add_team_member.html', {
        'form': form,
        'project': project
    })