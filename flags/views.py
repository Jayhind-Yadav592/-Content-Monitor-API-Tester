from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Flag
from .serializers import FlagSerializer, FlagStatusUpdateSerializer


class FlagListView(generics.ListAPIView):
    """
    PDF Requirement: GET /flags/ — List all generated flags
    Returns flags ordered by score (highest first)
    """
    queryset = Flag.objects.select_related('keyword', 'content_item').all()
    serializer_class = FlagSerializer


class FlagStatusUpdateView(generics.UpdateAPIView):
    """
    PATCH /flags/{id}/ — Update flag review status.
    Records reviewed_at timestamp for suppression logic.
    """
    queryset = Flag.objects.all()
    serializer_class = FlagStatusUpdateSerializer
    http_method_names = ['patch']

    def partial_update(self, request, *args, **kwargs):
        flag = self.get_object()
        serializer = self.get_serializer(flag, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data.get('status')

        # Record when reviewer made the decision (used for suppression)
        if new_status in [Flag.STATUS_RELEVANT, Flag.STATUS_IRRELEVANT]:
            flag.reviewed_at = timezone.now()

        flag.status = new_status
        flag.save()

        return Response(
            {
                "message": f"Flag status updated to '{new_status}'",
                "flag": FlagSerializer(flag).data
            },
            status=status.HTTP_200_OK
        )
