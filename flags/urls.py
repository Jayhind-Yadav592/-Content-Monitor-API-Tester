from django.urls import path
from .views import FlagListView, FlagStatusUpdateView

urlpatterns = [
    path('', FlagListView.as_view(), name='flag-list'),
    path('<int:pk>/', FlagStatusUpdateView.as_view(), name='flag-update'),
]
