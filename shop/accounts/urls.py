from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('about/',views.about_view, name='about'),
    path('expenses/',views.expenses_view, name='expenses'),
    path('greeting/', views.greeting_view, name='greeting'),
    path("owner/dashboard/", views.owner_dashboard, name="owner_dashboard"),
    path("staff/dashboard/", views.staff_dashboard, name="staff_dashboard"),
    path("dashboard/", views.dashboard_redirect, name="dashboard"),
    path('activity/', views.activity_view, name='activity'),
]
