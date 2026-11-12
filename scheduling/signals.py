from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

ROLE_GROUPS = ('Admin', 'Doctor', 'Receptionist')


@receiver(post_migrate)
def ensure_default_groups(sender, **kwargs):
    if sender.label != 'scheduling':
        return
    for group_name in ROLE_GROUPS:
        Group.objects.get_or_create(name=group_name)
