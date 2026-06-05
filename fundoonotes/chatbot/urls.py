from django.urls import path
from . import views

urlpatterns = [
    path("chat/", views.chat, name="chatbot-chat"),
    path("suggestions/", views.suggestions, name="chatbot-suggestions"),
    path("analyse-file/", views.analyse_file, name="chatbot-analyse-file"),
]
