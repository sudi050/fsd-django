from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name = 'main'),
    path('result/', views.result, name = 'result'),
    path('process_image/', views.process_image, name='process_image'),
    path('login/',views.login,name='login'),
    path('logout/', views.logout, name="logout"),
    path('signup/',views.signup,name='signup'),
]