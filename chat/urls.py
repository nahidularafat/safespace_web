# chat/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='chat/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Chat
    path('', views.chat_interface, name='home'),
    path('chat/<int:session_id>/', views.chat_interface, name='chat_interface_with_id'),
    path('new/', views.new_chat, name='new_chat'),
    path('api/send/', views.send_message, name='send_message'),
    
    # Dashboard & Portal routes
    path('dashboard/', views.mood_dashboard, name='mood_dashboard'), 
    path('therapist-portal/', views.therapist_portal, name='therapist_portal'), # <-- New Route
    path('predict-stress/', views.stress_prediction_view, name='predict_stress'),
]