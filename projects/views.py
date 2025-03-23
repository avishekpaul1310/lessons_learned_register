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
        'by_category': project.lessons.values('category__name').annotate(count=Count('category')),
        'by_status': project.lessons.values('status').annotate(count=Count('status')),
    }
    
    context = {
        'project': project,
        'user_role': user_role,
        'lesson_stats': lesson_stats,
        'team_members': ProjectRole.objects.filter(project=project).select_related('user'),
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