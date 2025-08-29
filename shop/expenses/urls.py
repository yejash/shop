from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.expenses_page, name='page'),
    # API endpoints:
    path('api/list/', views.api_list_expenses, name='api_list'),
    path('api/add/', views.api_add_expense, name='api_add'),
    path('api/update/', views.api_update_expense, name='api_update'),
    path('api/delete/', views.api_delete_expense, name='api_delete'),
    path("export/excel/", views.export_expenses_excel, name="export_expenses_excel"),
    path("export/pdf/", views.export_expenses_pdf, name="export_expenses_pdf"),
]
