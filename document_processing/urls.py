from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.upload_file_view),
    path('status/<str:id>', views.check_status_view),
    # path("file/<str:id>", views.download_file_view)
]