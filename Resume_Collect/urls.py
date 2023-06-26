from django.urls import path
from . import views

urlpatterns = [
    path('', views.Landing, name="Landing"),
    path('Register/', views.Register, name="Register"),
    path('Access/', views.Access, name="Access"),
    path('Collection/', views.Collection, name="Collection"),
    path('Exit', views.Exit, name="Exit")
]