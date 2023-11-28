from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.Document_save, name="upload"),
    path("process/<str:pk>/", views.Process, name="process"),
    path("results/<str:pk>/", views.processed_data, name="results")
    ]