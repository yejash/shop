from django.urls import path
from . import views

urlpatterns = [
    path('', views.income_list, name='income'),          # HTML page
    path('api/list/', views.api_list, name='income_api_list'),
    path('api/add/', views.api_add, name='income_api_add'),
    path('api/update/', views.api_update, name='income_api_update'),
    path('api/delete/', views.api_delete, name='income_api_delete'),
    path("export/excel/", views.export_income_excel, name="export_income_excel"),
    path("export/pdf/", views.export_income_pdf, name="export_income_pdf"),
]
