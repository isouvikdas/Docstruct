import json
import hashlib
from datetime import timedelta
from django.utils import timezone
from .exception import IdempotencyKeyMismatch, IdempotencyInProgress

from .models import IdempotencyRecord

def store_idem(key: str, endpoint: str, request_body: dict):
    """Args: Expiry time in hours"""

    now = timezone.now()

    IdempotencyRecord.objects.create(
        key=key,
        endpoint=endpoint,
        expires_at=now + timedelta(hours=24),
        created_at=now,
        request_hash=hash_payload(request_body),
        state='PROCESSING'
    )

def update_idem(key: str, status_code: int, response_body: dict, state: str):
    idem = IdempotencyRecord.objects.filter(key=key).first()
    if idem:
        idem.objects.update(status_code=status_code, response_body=response_body, state=state)
    else:
        raise

def claim_idem_or_create(
    key: str,
    endpoint: str,
    request_body: dict
) -> IdempotencyRecord | None:

    idem = IdempotencyRecord.objects.filter(key=key).first()

    if idem:
        request_hash = hash_payload(request_body)

        if request_hash != idem.request_hash or endpoint != idem.endpoint:
            raise IdempotencyKeyMismatch()

        if idem.state == "PROCESSING":
            raise IdempotencyInProgress()

        if idem.state == "COMPLETED":
            return idem

    store_idem(key, endpoint, request_body)
    return None


def hash_payload(payload: dict) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separator=(",", ":")
    )

    return hashlib.sha256(
        canonical.encode('utf-8')
    ).hexdigest()
