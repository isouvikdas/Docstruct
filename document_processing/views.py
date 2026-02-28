from rest_framework import response, status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
import logging


from . import storage, tasks
from .models import Document
from .serializers import DocumentSerializer

logger = logging.getLogger(__name__)


# Create your views here.

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_file_view(request):
    try:
        file = request.FILES.get('file')
        if not file:
            return response.Response(
                {"error": "No file provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        saved_file = storage.upload_file(file, file.name, file.size)
        if saved_file is None:
            return response.Response(
                {"error": "unable to save file"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        saved_document = Document.objects.create(
            file_key=saved_file.file_key,
            original_filename=saved_file.original_filename,
            file_url=saved_file.file_url,
            file_size=saved_file.file_size,
            status='PENDING'
        )
        serializer = DocumentSerializer(saved_document)
        tasks.process_file.delay(saved_document.id)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(e)
        return response.Response(
            {"error": "Internal Server Error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_status_view(request, id):
    try:
        document = Document.objects.get(id=id)
        serializer = DocumentSerializer(document)
        return response.Response({"message": "Success", "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(e)
        return response.Response(
            {"error": "Internal Server Error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
