from django.contrib import admin
from .models import Profile, AllowedEmailDomain

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'job_title', 'department')
    search_fields = ('user__username', 'user__email', 'job_title', 'department')

class AllowedEmailDomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'description', 'is_active', 'date_added')
    list_filter = ('is_active',)
    search_fields = ('domain', 'description')
    readonly_fields = ('date_added', 'last_modified')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(AllowedEmailDomain, AllowedEmailDomainAdmin)