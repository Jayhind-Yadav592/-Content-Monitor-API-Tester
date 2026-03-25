from django.urls import path
from .views import ScanView, LoadMockDataView

urlpatterns = [
    path('', ScanView.as_view(), name='scan'),
    path('load-mock/', LoadMockDataView.as_view(), name='load-mock'),
]
