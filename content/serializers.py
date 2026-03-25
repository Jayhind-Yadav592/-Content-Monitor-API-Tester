from rest_framework import serializers
from .models import ContentItem


class ContentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentItem
        fields = ['id', 'title', 'source', 'body', 'last_updated', 'created_at']
        read_only_fields = ['id', 'created_at']
