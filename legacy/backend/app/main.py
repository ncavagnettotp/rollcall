import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from .database import probe_database
from .documents import router as documents_router
from .inventory import router as inventory_router
from .document_store import StoreUnavailable, DocumentNotFound, RevisionConflict

load_dotenv(Path(__file__).resolve().parents[1] / '.env')
app = FastAPI(title='Tire & Wheel Storage — Document Review', version='0.2.0')
app.include_router(documents_router)
app.include_router(inventory_router)

@app.exception_handler(StoreUnavailable)
async def archive_unavailable(request: Request, exc: StoreUnavailable):
    return JSONResponse(status_code=503, content={'detail': 'Document archive unavailable. Check the database, migration, and archive folder.'})

@app.exception_handler(DocumentNotFound)
async def document_not_found(request: Request, exc: DocumentNotFound):
    return JSONResponse(status_code=404, content={'detail': 'Document not found.'})

@app.exception_handler(RevisionConflict)
async def review_conflict(request: Request, exc: RevisionConflict):
    return JSONResponse(status_code=409, content={'detail': 'This review changed in another session. Reload it before saving.'})
CATEGORIES = ['Stored', 'Due Soon', 'Overdue', 'Needs Attention']

class DatabaseUnavailable(Exception):
    pass

def check_database():
    try:
        url = os.environ.get('DATABASE_URL', '')
        if not url.startswith(('postgresql://', 'postgres://')) or not probe_database(url):
            raise DatabaseUnavailable()
        return True
    except Exception:
        raise DatabaseUnavailable() from None

@app.exception_handler(DatabaseUnavailable)
async def database_unavailable(request: Request, exc: DatabaseUnavailable):
    return JSONResponse(status_code=503, content={'status': 'unavailable', 'database': 'postgresql'})

@app.get('/api/health')
def health():
    return {'status': 'ok'}

@app.get('/api/health/db')
def database_health(connected: bool = Depends(check_database)):
    return {'status': 'ok', 'database': 'postgresql'}

@app.get('/api/dashboard')
def dashboard():
    return {'counts_are_placeholders': True, 'categories': [{'label': label, 'count': None} for label in CATEGORIES]}
