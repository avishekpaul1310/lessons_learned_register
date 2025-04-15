from django.conf import settings
from django.core.cache import cache
from .models import AllowedEmailDomain

def get_allowed_email_domains():
    """
    Get allowed email domains from the database, with fallback to settings.py
    Uses caching to avoid frequent database queries
    """
    # Try to get from cache first
    domains = cache.get('allowed_email_domains')
    if domains is None:
        # If not in cache, query the database
        domains = list(AllowedEmailDomain.objects.filter(is_active=True).values_list('domain', flat=True))
        
        # If database has no domains, use fallback from settings
        if not domains:
            domains = getattr(settings, 'ALLOWED_EMAIL_DOMAINS', [])
        
        # Cache the results for 1 hour (3600 seconds)
        cache.set('allowed_email_domains', domains, 3600)
    
    return domains