from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = "home"),
    path('packages/', views.packages, name = "packages"),
    path('trucks/', views.trucks, name = "trucks"),

    path('login/', views.loginPage, name = "login"),
    path('register/', views.registerPage, name = "register"),
    path('logout/', views.logoutUser, name="logout"),
    path('pending/', views.pending, name = "pending"),
    path('update/<str:pk>/', views.update, name="update"),
    path('customer/', views.customer, name = "customer"),
    path('sent/', views.sent, name="sent"),
    path('tracking/', views.tracking, name="tracking")
]      