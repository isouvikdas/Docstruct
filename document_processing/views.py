from rest_framework import response, status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .llm import LLM
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
        logger.info(f"Uploaded file: {saved_file.original_filename}")
        saved_document = Document.objects.create(
            user = request.user,
            file_key=saved_file.file_key,
            original_filename=saved_file.original_filename,
            file_url=saved_file.file_url,
            file_size=saved_file.file_size,
            status='PENDING',
            is_embedded=False
        )
        serializer = DocumentSerializer(saved_document)
        tasks.process_file.delay(saved_document.id)
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.exception(e)
        return response.Response(
            {"error": "Internal Server Error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ask_question_view(request):
    try:
        doc_id = request.data.get('doc_id')
        query = request.data.get('query')
        if doc_id and doc_id != "":
            document = Document.objects.get(id = doc_id)
            if not document or document.user.id != request.user.id:
                return response.Response(
                    {"error": "No document found with this id"},
                    status=status.HTTP_404_NOT_FOUND
                )
        if not query or query == "":
            return response.Response(
                {"error": "No query provided"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if doc_id and doc_id != "" and query and query != "":
            query = f"{query}, document id: {doc_id}, user id: {request.user.id}"
        llm = LLM()
        reply = llm.ask_llm(str(query))
        return response.Response({"message": "Success", "data": reply}, status=status.HTTP_200_OK)
    except Exception as e:
        return response.Response(
            {"error": "Internal Server Error"},
            status = status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def check_status_view(request, id):
    try:
        document = Document.objects.get(id=id)
        if document.user.id != request.user.id:
            return response.Response({"message": "You are not authorized to view this document"}, status=status.HTTP_403_FORBIDDEN)
        serializer = DocumentSerializer(document)
        return response.Response({"message": "Success", "data": serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.exception(e)
        return response.Response(
            {"error": "Internal Server Error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )