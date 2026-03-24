from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctor/<int:doctor_id>/', views.doctor_detail, name='doctor_detail'),
    path('book/<int:slot_id>/', views.book_appointment, name='book_appointment'),
]
