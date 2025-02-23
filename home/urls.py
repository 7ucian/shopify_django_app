from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='root_path'),
    path('upload/', views.upload_document, name='upload_document'),
]
