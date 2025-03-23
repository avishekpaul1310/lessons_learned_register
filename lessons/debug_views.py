# Add this to a new file in the lessons app (lessons/debug_views.py)

from django.http import HttpResponse
from django.conf import settings
import os

def debug_view(request):
    """
    A simple view that displays debug information about the Django environment.
    """
    response = []
    
    # Basic info
    response.append("<h1>Debug Information</h1>")
    
    # Template directories
    response.append("<h2>Template Directories</h2>")
    response.append("<ul>")
    for template_dir in settings.TEMPLATES[0]['DIRS']:
        response.append(f"<li>{template_dir}</li>")
    response.append("</ul>")
    
    # Check if specific templates exist
    template_paths = [
        os.path.join(settings.BASE_DIR, 'templates', 'base.html'),
        os.path.join(settings.BASE_DIR, 'templates', 'accounts', 'login.html'),
        os.path.join(settings.BASE_DIR, 'templates', 'accounts', 'register.html')
    ]
    
    response.append("<h2>Template Files</h2>")
    response.append("<ul>")
    for path in template_paths:
        exists = os.path.exists(path)
        status = "EXISTS" if exists else "MISSING"
        color = "green" if exists else "red"
        response.append(f'<li style="color: {color}">{path} - {status}</li>')
    response.append("</ul>")
    
    # Static files
    response.append("<h2>Static Files Configuration</h2>")
    response.append("<ul>")
    response.append(f"<li>STATIC_URL: {settings.STATIC_URL}</li>")
    response.append(f"<li>STATICFILES_DIRS: {settings.STATICFILES_DIRS if hasattr(settings, 'STATICFILES_DIRS') else 'Not set'}</li>")
    response.append(f"<li>STATIC_ROOT: {settings.STATIC_ROOT if hasattr(settings, 'STATIC_ROOT') else 'Not set'}</li>")
    response.append("</ul>")
    
    # Media files
    response.append("<h2>Media Files Configuration</h2>")
    response.append("<ul>")
    response.append(f"<li>MEDIA_URL: {settings.MEDIA_URL}</li>")
    response.append(f"<li>MEDIA_ROOT: {settings.MEDIA_ROOT}</li>")
    response.append("</ul>")
    
    # Installed apps
    response.append("<h2>Installed Apps</h2>")
    response.append("<ul>")
    for app in settings.INSTALLED_APPS:
        response.append(f"<li>{app}</li>")
    response.append("</ul>")
    
    return HttpResponse("".join(response))