from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import run_scan, load_mock_data


class ScanView(APIView):

    def post(self, request):
        result = run_scan()
        return Response(result, status=status.HTTP_200_OK)


class LoadMockDataView(APIView):

    def post(self, request):
        result = load_mock_data()
        return Response(result, status=status.HTTP_200_OK)
