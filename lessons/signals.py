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
                'site_url': settings.SITE_URL,
            })
            
            plain_message = strip_tags(html_message)
            
            # Send to each tagged user
            recipient_list = [user.email for user in tagged_users if user.email]
            if recipient_list:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    recipient_list,
                    html_message=html_message,
                )

@receiver(post_save, sender=Comment)
def notify_lesson_owner(sender, instance, created, **kwargs):
    if created:
        lesson = instance.lesson
        # Only notify if the comment author is not the lesson submitter
        if instance.author != lesson.submitted_by:
            subject = f'New comment on your lesson: {lesson.title}'
            
            html_message = render_to_string('lessons/email/comment_notification.html', {
                'lesson': lesson,
                'comment': instance,
                'author': instance.author,
                'site_url': settings.SITE_URL,
            })
            
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [lesson.submitted_by.email],
                html_message=html_message,
            )