from rest_framework import generics, status
from rest_framework.response import Response
from .models import Keyword
from .serializers import KeywordSerializer


class KeywordListCreateView(generics.ListCreateAPIView):
    """
    PDF Requirement: POST /keywords/ — Create a keyword
    Also supports GET /keywords/ to list all keywords
    """
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                "message": "Keyword created successfully",
                "keyword": serializer.data
            },
            status=status.HTTP_201_CREATED
        )
