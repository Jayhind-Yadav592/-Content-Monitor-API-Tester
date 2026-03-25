from django.urls import path
from .views import ContentItemListView

urlpatterns = [
    path('', ContentItemListView.as_view(), name='content-list'),
]
