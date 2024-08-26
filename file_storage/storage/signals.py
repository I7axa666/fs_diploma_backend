from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import File, UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

@receiver(post_save, sender=File)
def update_user_file_stats_on_create(sender, instance, created, **kwargs):
    if created:
        user_profile, _ = UserProfile.objects.get_or_create(user=instance.user)
        user_profile.file_count += 1
        user_profile.total_file_size += instance.size
        user_profile.save()

@receiver(post_delete, sender=File)
def update_user_file_stats_on_delete(sender, instance, **kwargs):
    user_profile, _ = UserProfile.objects.get_or_create(user=instance.user)
    user_profile.file_count = max(0, user_profile.file_count - 1)
    user_profile.total_file_size = max(0, user_profile.total_file_size - instance.size)
    user_profile.save()