from django.urls import path
from .views import note_detail, notes_list_create

urlpatterns = [
    path("", notes_list_create, name="notes-list-create"),
    path("<int:pk>/", note_detail, name="note-detail"),
]
