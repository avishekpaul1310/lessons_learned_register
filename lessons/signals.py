from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Lesson, Comment

@receiver(post_save, sender=Lesson)
def notify_tagged_users(sender, instance, created, **kwargs):
    if created:
        # Email tagged users
        tagged_users = instance.tags.all()
        if tagged_users:
            subject = f'You were tagged in a lesson: {instance.title}'
            
            html_message = render_to_string('lessons/email/tagged_notification.html', {
                'lesson': instance,
                'project': instance.project,
                'submitted_by': instance.submitted_by,
            })
            
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.submitted_by.email],
                html_message=html_message,
            )