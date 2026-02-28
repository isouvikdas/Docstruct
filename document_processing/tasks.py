import os.path

from celery import shared_task
from .ocr import read_image, convert_pdf
from .models import Document
from . import storage
from io import BytesIO
from PIL import Image
import logging
from . import llm
logger = logging.getLogger(__name__)

@shared_task
def process_file(document_id):
    try:
        document = Document.objects.get(id=document_id)
        document.status = "PROCESSING"
        document.save()
        name, ext = os.path.splitext(document.original_filename)
        print(document.original_filename)
        print(name)
        print(ext)
        if ext == ".pdf":
            print("entered pdf")
            path = storage.download_pdf(document.file_key)
            # print(path)
            text = convert_pdf(path)
            os.remove(path)
        else :
            image_bytes = storage.download_image(document.file_key)
            image = Image.open(BytesIO(image_bytes))
            text = read_image(image)
        if text is not None:
            document.extracted_text = text
        else:
            document.status = "FAILED"
            document.error_text = "OCR extraction failed"
            document.save()
            return
        document.save()
        print("reached here")
        data = llm.get_data(text)
        print(data)
        if data is not None:
            document.status = "COMPLETED"
            document.extracted_data = data
            document.save()
        else:
            document.status = "FAILED"
            document.error_text = "LLM extraction failed"
            document.save()
            return
    except Exception as e:
        Document.objects.filter(id=document_id).update(
            status="FAILED",
            error_text=str(e)
        )