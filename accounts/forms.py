from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from .models import Profile
from .utils import get_allowed_email_domains

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            domain = email.split('@')[-1]
            allowed_domains = get_allowed_email_domains()
            
            if allowed_domains and domain not in allowed_domains:
                allowed_domains_str = ', '.join(allowed_domains[:5])
                if len(allowed_domains) > 5:
                    allowed_domains_str += f" and {len(allowed_domains) - 5} more"
                raise forms.ValidationError(
                    f"Registration is restricted to approved email domains. Currently allowed: {allowed_domains_str}"
                )
        return email

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            domain = email.split('@')[-1]
            allowed_domains = get_allowed_email_domains()
            
            if allowed_domains and domain not in allowed_domains:
                allowed_domains_str = ', '.join(allowed_domains[:5])
                if len(allowed_domains) > 5:
                    allowed_domains_str += f" and {len(allowed_domains) - 5} more"
                raise forms.ValidationError(
                    f"Email addresses must use an approved domain. Currently allowed: {allowed_domains_str}"
                )
        return email

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'job_title', 'department']