from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from .models import Event


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    """Send activation email when a new user is created"""
    if created and not instance.is_active:
        # Generate activation token
        token = default_token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))

        # Create activation link
        activation_link = f"{settings.SITE_URL}{reverse('activate_account', kwargs={'uidb64': uid, 'token': token})}"

        # Send activation email
        try:
            send_mail(
                subject='Activate Your Account',
                message=f'Hi {instance.get_full_name() or instance.username},\n\n'
                       f'Thank you for registering! Please click the link below to activate your account:\n\n'
                       f'{activation_link}\n\n'
                       f'If you didn\'t create this account, please ignore this email.\n\n'
                       f'Best regards,\nEvent Management Team',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Activation email sending failed: {e}")


@receiver(m2m_changed, sender=Event.participants.through)
def send_rsvp_notification(sender, instance, action, pk_set, **kwargs):
    """Send email notification when a user RSVPs to an event"""
    if action == 'post_add':
        for user_id in pk_set:
            try:
                user = User.objects.get(pk=user_id)
                send_mail(
                    subject=f'RSVP Confirmation: {instance.name}',
                    message=f'Hi {user.get_full_name() or user.username},\n\n'
                           f'You have successfully RSVP\'d to the following event:\n\n'
                           f'Event: {instance.name}\n'
                           f'Date: {instance.date}\n'
                           f'Time: {instance.time}\n'
                           f'Location: {instance.location}\n\n'
                           f'Thank you for your interest!\n\n'
                           f'Best regards,\nEvent Management Team',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            except User.DoesNotExist:
                continue
            except Exception as e:
                print(f"RSVP notification email sending failed: {e}")