from typing import Dict

from django.http import HttpRequest


def role_flags(request: HttpRequest) -> Dict[str, bool]:
    """
    Inject convenient booleans for role-based navigation into every template.
    """
    if not request.user.is_authenticated:
        return {
            'is_admin_user': False,
            'is_doctor_user': False,
            'is_receptionist_user': False,
        }

    user = request.user
    group_names = set(user.groups.values_list('name', flat=True))
    return {
        'is_admin_user': user.is_superuser or 'Admin' in group_names,
        'is_doctor_user': 'Doctor' in group_names,
        'is_receptionist_user': 'Receptionist' in group_names,
    }
