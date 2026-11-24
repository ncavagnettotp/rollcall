# Stage 2 upload and review — November 10, 2026

User authorized Stage 2 after accepting Stage 1 and clarifying eight sample PDFs. Implement a simple dark upload/review page in the existing React/FastAPI application. Store original PDFs on local disk and document metadata/extracted fields/corrections in PostgreSQL. Apply schema explicitly through a migration command, never silently at app startup.

Scope: upload digital PDF, extract readable text and fields, preserve evidence, display warnings, correct/save review, reopen archived originals/reviews, prevent exact-file duplicate archives. No OCR, business set/period changes, confirmed swaps, full VIN matching, payments, staff accounts, or automatic startup. Label action suggestions as preliminary; data missing from a PDF remains missing. Current shop-local date is a labeled fallback; invoice dates supersede authorizations when later business-event linking is implemented. Stage 2 stores separate source documents and flags related work orders; it does not repeat or implement business events.

Chosen approach: native React form plus FastAPI/PostgreSQL document archive. Reuse installed pypdf for digital text; no AI service/external document transmission. Alternatives: browser-only preview cannot persist shared reviews; implementing full storage actions now breaks stage boundaries. Keep upload as a dedicated page so dashboard stays uncluttered.

## Shared API contract

- POST /api/documents: raw PDF bytes, Content-Type application/pdf, X-Filename URI-encoded basename. Max 10 MiB; validate PDF/encryption/pages/text. Return document JSON; exact sha256 repeat returns same id with duplicate=true. Scanned/no-text valid PDFs are retained with explicit needs-review warning; malformed/encrypted rejected clearly. Original documents stay available for manual review.
- GET /api/documents: {documents: [document JSON]}, newest first (bounded list).
- GET /api/documents/{id}: document JSON.
- GET /api/documents/{id}/pdf: archived original PDF.
- PATCH /api/documents/{id}: {version: integer, fields: object, status: 'reviewed'}; require optimistic revision; preserve extracted unchanged. Return updated document; stale version 409.

Document JSON: {id, filename, pages, extracted: fields, fields: fields, warnings: string[], status: 'needs_review'|'reviewed', version: integer, duplicate: boolean, pdf_url, created_at}.

fields keys (all strings): document_type, invoice_number, work_order_number, customer_name, contact, vehicle, vin, start_date (YYYY-MM-DD), date_source, storage_description, notes, action, centering_rings, lug_nuts, center_caps. Unknown accessories use 'unknown'; chosen values 'yes'/'no'. action suggestions: 'review_required', 'storage', 'swap', 'retrieval', 'renewal', 'purchase_only'. Preserve invoice identity from PDF, not filename. Conflicting/ambiguous fields require warnings, never silent guess. Keep source snippets/whole extracted text in extracted evidence if useful, without leaking raw text to logs.

## Ownership and verification

Backend agent owns backend app document/parser modules, migration utility, backend requirements/tests. UI agent owns frontend and tests. Coordinator owns integration, docs, browser acceptance, checkpoints. Test eight real PDFs, document date vs export dates, page-spanning packages, pickup/no-renewal, no-package retrieval, purchase-only, staggered sizes, unknown accessories, malformed/no-text, duplicates, archived originals, corrections/revision conflict and restart/reopen durability. Use existing dev database only for explicit document schema, never mutate unrelated tables or installed service. Keep sample PDFs, extracted customer data, and archive directories out of source checkpoints.
