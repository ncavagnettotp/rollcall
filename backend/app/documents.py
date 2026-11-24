"""Raw PDF upload/review API. Saving a review never changes storage records."""
from datetime import date
import re
from typing import Literal
from urllib.parse import unquote
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field, StrictStr, field_validator
from starlette.concurrency import run_in_threadpool

from . import document_store as store
from .document_parser import ACTIONS, FIELD_KEYS, InvalidPDF, extract_pdf

router = APIRouter(prefix='/api/documents')
MAX_BYTES = 10 * 1024 * 1024


class Review(BaseModel):
    model_config = ConfigDict(extra='forbid')
    version: int = Field(ge=1, strict=True)
    fields: dict[str, StrictStr]
    status: Literal['reviewed']

    @field_validator('fields')
    @classmethod
    def check_fields(cls, fields):
        if set(fields) - set(FIELD_KEYS):
            raise ValueError('Unknown review field.')
        if any(len(value) > 10000 for value in fields.values()):
            raise ValueError('Review field too long.')
        for key in ('centering_rings', 'lug_nuts', 'center_caps'):
            if key in fields and fields[key] not in ('unknown', 'yes', 'no'):
                raise ValueError('Accessory must be unknown, yes, or no.')
        if 'action' in fields and fields['action'] not in ACTIONS:
            raise ValueError('Unknown action suggestion.')
        if 'document_type' in fields and fields['document_type'] not in ('unknown', 'invoice', 'authorization', 'work_order'):
            raise ValueError('Unknown document type.')
        if fields.get('start_date'):
            parsed = date.fromisoformat(fields['start_date'])
            if parsed.isoformat() != fields['start_date']:
                raise ValueError('Use YYYY-MM-DD.')
        if fields.get('vin') and not re.fullmatch(r'[A-HJ-NPR-Z0-9]{17}', fields['vin'], re.I):
            raise ValueError('VIN must contain 17 valid VIN characters or remain blank.')
        return fields


def safe_filename(raw: str) -> str:
    name = re.split(r'[/\\]', unquote(raw))[-1]
    name = re.sub(r'[\x00-\x1f\x7f]', '', name).strip()[:200]
    return name or 'document.pdf'


@router.post('')
async def upload(request: Request):
    if request.headers.get('content-type', '').split(';')[0].strip().lower() != 'application/pdf':
        raise HTTPException(415, 'Upload a PDF using application/pdf.')
    length = request.headers.get('content-length', '')
    if length.isdecimal() and int(length) > MAX_BYTES:
        raise HTTPException(413, 'PDF must be 10 MiB or smaller.')
    content = bytearray()
    async for chunk in request.stream():
        if len(content) + len(chunk) > MAX_BYTES:
            raise HTTPException(413, 'PDF must be 10 MiB or smaller.')
        content.extend(chunk)
    try:
        fields, warnings, pages, text = await run_in_threadpool(extract_pdf, bytes(content))
    except InvalidPDF as error:
        raise HTTPException(422, str(error)) from None
    return await run_in_threadpool(store.persist, bytes(content),
                                   safe_filename(request.headers.get('x-filename', 'document.pdf')),
                                   fields, warnings, pages, text)


@router.get('')
def listing():
    return {'documents': store.list_documents()}


@router.get('/{document_id}')
def details(document_id: UUID):
    return store.get_document(document_id)


@router.get('/{document_id}/pdf')
def original(document_id: UUID):
    path, filename = store.get_document(document_id, original=True)
    return FileResponse(path, media_type='application/pdf', filename=filename, content_disposition_type='inline',
                        headers={'X-Content-Type-Options': 'nosniff'})


@router.patch('/{document_id}')
def review(document_id: UUID, change: Review):
    return store.save_review(document_id, change.version, change.fields)
