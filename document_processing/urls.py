from django.urls import path
from . import views

urlpatterns = [
    path('upload', views.upload_file_view),
    path('status/<str:id>', views.check_status_view),
    path('chat', views.ask_question_view)
]