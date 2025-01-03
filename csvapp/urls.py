from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('manipulate_dataset/',views.manipulate_dataset,name = 'manipulate_dataset'),
    path('process_dataset/', views.process_dataset, name='process_dataset'),
    path('visualization/',views.generate_visualization,name='visualization')
]