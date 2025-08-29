# from django.db import models

# class Profile(models.Model):
#     name = models.CharField(max_length=100)
#     email = models.EmailField()

#     def __str__(self):
#         return self.name

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

def validate_avatar_size(file):
    limit = 1024 * 1024  # 1 MB
    if file.size > limit:
        raise ValidationError("Avatar file too large (max 1 MB).")


class Profile(models.Model):
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('staff', 'Staff'),
    ]
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True,validators=[FileExtensionValidator(['jpg','jpeg','png','gif']), validate_avatar_size])
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')

    def __str__(self):
        return f"{self.user.username} ({self.role})"
    
    
class Transaction(models.Model):
    TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    mode = models.CharField(max_length=50, blank=True, null=True)  # e.g. Cash, Bank

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)

