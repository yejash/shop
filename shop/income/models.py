from django.conf import settings
from django.db import models

MODE_CHOICES = [
    ('cash', 'Cash'),
    ('d_cash', 'D_Cash'),
    ('icici', 'ICICI'),
    ('idfc', 'IDFC'),
    ('sbi', 'SBI'),
    ('alpha', 'Alpha'),
    ('hdfc', 'HDFC'),
]

class Income(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=255)
    mode = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    # add this:
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user} — {self.amount} on {self.date}"