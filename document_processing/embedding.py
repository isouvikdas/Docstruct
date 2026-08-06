from celery import shared_task

from .models import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as DC
from dotenv import load_dotenv
from .vector_store import vector_store
import logging

logger = logging.getLogger(__name__)

load_dotenv()

@shared_task
def embed_documents(doc_id: str):
    try:
        doc = Document.objects.get(id=doc_id)

        metadata = {
            "user_id": str(doc.user.id),
            "document_id": str(doc.id),
            "filename": doc.original_filename,
        }

        document = DC(
            page_content=str(doc.extracted_data),
            metadata=metadata,
        )

        if len(document.page_content) <= 4000:
            all_splits = [document]
        else:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=200,
                separators=["\n\n", "\n", ". ", " ", ""],
            )
            all_splits = text_splitter.split_documents([document])

        logger.info(f"Prepared {len(all_splits)} chunks for embedding.")
        logger.info(
            f"Total characters: {sum(len(d.page_content) for d in all_splits)}"
        )
        vector_store.add_documents(all_splits)

        logger.info(f"Indexed {len(all_splits)} chunks.")

        doc.is_embedded = True
        doc.error_text = ""
        doc.save(update_fields=["is_embedded", "error_text"])
        logger.info("Invoice saved")

    except BaseException as e:
        Document.objects.filter(id = doc_id).update(error_text = str(e))
        logger.exception("Failed to embed document %s", doc_id)
