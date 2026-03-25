from rest_framework import generics
from .models import ContentItem
from .serializers import ContentItemSerializer

class ContentItemListView(generics.ListAPIView):
    queryset = ContentItem.objects.all()
    serializer_class = ContentItemSerializer
