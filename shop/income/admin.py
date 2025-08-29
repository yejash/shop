from django.contrib import admin
from .models import Income

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'date', 'description', 'mode', 'amount')
    list_filter = ('mode','date')
    search_fields = ('description', 'user__username')
