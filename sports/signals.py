from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth.models import Group
from allauth.account.signals import user_signed_up

@receiver(user_signed_up)
def populate_profile(request, user, **kwargs):
    socialaccount = user.socialaccount_set.filter(provider='google').first()
    if socialaccount:
        data = socialaccount.extra_data
        user.email = data.get('email', '')
        user.real_name = data.get('name', '')
        user.date_joined_pma = timezone.now()
        user.save()

@receiver(user_signed_up)
def assign_default_group(sender, request, user, **kwargs):
    regular_group, created = Group.objects.get_or_create(name='Common')
    user.groups.add(regular_group)
    user.save()