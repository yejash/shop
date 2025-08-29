# accounts/context_processors.py
from .models import Profile

def user_profile(request):
    prof = None
    if request.user.is_authenticated:
        try:
            prof = request.user.profile
        except Profile.DoesNotExist:
            prof = None
    return {"profile": prof}
