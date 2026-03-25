from rest_framework import serializers
from .models import Flag


class FlagSerializer(serializers.ModelSerializer):
    keyword_name = serializers.CharField(source='keyword.name', read_only=True)
    content_title = serializers.CharField(source='content_item.title', read_only=True)
    content_source = serializers.CharField(source='content_item.source', read_only=True)

    class Meta:
        model = Flag
        fields = [
            'id',
            'keyword',
            'keyword_name',
            'content_item',
            'content_title',
            'content_source',
            'score',
            'status',
            'reviewed_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'keyword', 'keyword_name',
            'content_item', 'content_title', 'content_source',
            'score', 'reviewed_at', 'created_at', 'updated_at'
        ]


class FlagStatusUpdateSerializer(serializers.ModelSerializer):
    """
    PDF Requirement: PATCH /flags/{id}/ — Update review status
    Only allows updating the status field (pending, relevant, irrelevant)
    """
    class Meta:
        model = Flag
        fields = ['status']

    def validate_status(self, value):
        allowed = [Flag.STATUS_PENDING, Flag.STATUS_RELEVANT, Flag.STATUS_IRRELEVANT]
        if value not in allowed:
            raise serializers.ValidationError(
                f"Status must be one of: {', '.join(allowed)}"
            )
        return value
