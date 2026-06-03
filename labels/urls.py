from django.urls import path

from .views import label_detail, labels_list_create

urlpatterns = [
    path("", labels_list_create, name="labels-list-create"),
    path("<int:pk>/", label_detail, name="label-detail"),
]
