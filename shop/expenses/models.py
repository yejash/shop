from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    MODE_CHOICES = [
        ('cash', 'Cash'),
        ('icici', 'ICICI'),
        ('d_cash', 'D_Cash'),
        ('idfc', 'IDFC'),
        ('sbi', 'SBI'),
        ('alpha', 'Alpha'),
        ('hdfc', 'HDFC'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    date = models.DateField()
    description = models.CharField(max_length=255)
    mode = models.CharField(max_length=30, choices=MODE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def as_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d'),
            'description': self.description,
            'mode': self.mode,
            'amount': str(self.amount),
        }

    def __str__(self):
        return f"{self.user.username} - {self.description} - {self.amount}"
