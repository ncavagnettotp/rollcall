"""Behavioral checks for invoice evidence; fixtures contain fictional identities."""
import importlib.util
import io
from datetime import date

from fastapi.testclient import TestClient
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, NameObject, DictionaryObject

from app.main import app


def parse(text):
    assert importlib.util.find_spec('app.document_parser'), 'PDF parser is not implemented'
    from app.document_parser import parse_text
    return parse_text(text, today=date(2026, 11, 10))


def test_invoice_header_date_beats_footer_and_id_comes_from_content():
    fields, warnings = parse('Invoice\nBill To Smith, Jane\nDescription 2020 Test Car\n'
                            'VIN 1HGCM82633A004352\nInvoice # 123456 Invoice Date 10/22/2026 6:49 PM\n'
                            'Work Order # 246408\n10/30/2026 9:01 PM Invoice #123456 Page 1 of 2')
    assert fields['invoice_number'] == '123456'
    assert fields['start_date'] == '2026-10-22'
    assert fields['date_source'] == 'Invoice Date'
    assert fields['vin'] == '1HGCM82633A004352'
    assert 'preliminary' in ' '.join(warnings).lower()


def test_authorization_falls_back_to_visible_shop_date_not_appointment():
    fields, warnings = parse('Authorization\nWork Order # 246537 Appointment 11/3/2026\n'
                            '10/30/2026 9:13 PM Work Order #246537 Page 1 of 2')
    assert fields['document_type'] == 'authorization'
    assert fields['start_date'] == '2026-11-10'
    assert fields['date_source'] == 'Current shop date (fallback)'
    assert 'fallback' in ' '.join(warnings).lower()


def test_page_spanning_storage_keeps_description_and_unknown_accessories():
    fields, _ = parse('Authorization\nWork Order # 99\nSeasonal Tire Rotation\n'
                      'Seasonal Tire Storage\nStore customers wheels/tires. 6 month maximum.\n'
                      'Lugs Y / N Center caps Y / N Center rings Y / N Notes__285/45R22 Michelin on Asanti wheels\n'
                      '10/30/2026 Work Order #99 Page 1 of 2\nStorage $99.99\n'
                      'Mount, Install & Balance 4 Tires\nDispose Continentals')
    assert fields['action'] == 'swap'
    assert 'Michelin' in fields['storage_description']
    assert fields['lug_nuts'] == fields['center_caps'] == fields['centering_rings'] == 'unknown'


def test_selected_accessories_and_replacement_note_survive_without_legal_boilerplate():
    fields, _ = parse('Invoice\nSeasonal Tire Rotation\nSeasonal Tire Storage\n'
                      'Store customers wheels/tires. 6 month maximum.\n'
                      'Lugs Y Center caps Y Center rings N Notes___ General G-Max 305/35R24 NEEDS TIRES REPLACED\n'
                      'Customer acknowledges and agrees that all property stored is at sole risk.\nStorage $99.99')
    assert fields['lug_nuts'] == fields['center_caps'] == 'yes'
    assert fields['centering_rings'] == 'no'
    assert 'NEEDS TIRES REPLACED' in fields['notes']
    assert 'sole risk' not in fields['notes']


def test_pickup_with_storage_charge_and_from_storage_without_package_are_retrieval():
    for text in ('Seasonal Tire Storage\nPickup\nStored since 11/7/2024\nStorage $199.98',
                 'Mount, Install & Balance 4 Tires\nInstall Tires From Storage / Discard Summers'):
        fields, _ = parse(text)
        assert fields['action'] == 'retrieval'


def test_renewal_seasons_warn_and_purchase_legal_storage_is_not_package():
    fields, warnings = parse('Seasonal Tire Storage\nPirelli 275/35R21 and 315/30R21\n'
                            'Payment for Winter 2025-2026 and Summer 2026\nStorage $199.98')
    assert fields['action'] == 'renewal'
    assert '275/35R21' in fields['storage_description']
    assert '315/30R21' in fields['storage_description']
    assert any('histor' in warning.lower() for warning in warnings)
    fields, _ = parse('Invoice\nTire & Wheel Package\nNitto tires\n'
                      'Repair Liens or Storage Liens Legislation.')
    assert fields['action'] == 'purchase_only'
    assert fields['storage_description'] == ''


def blank_pdf(pages=1, encrypted=False):
    writer = PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=600, height=800)
    if encrypted:
        writer.encrypt('secret')
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def test_pdf_validation_keeps_blank_reviewable_and_rejects_invalid_encrypted_many_pages():
    assert importlib.util.find_spec('app.document_parser'), 'PDF validation is not implemented'
    from app.document_parser import extract_pdf, InvalidPDF
    import pytest
    fields, warnings, pages, text = extract_pdf(blank_pdf())
    assert pages == 1 and fields['action'] == 'review_required'
    assert any('text' in warning.lower() for warning in warnings)
    for content in (b'%PDF-this-is-broken', blank_pdf(encrypted=True), blank_pdf(51)):
        with pytest.raises(InvalidPDF):
            extract_pdf(content)


def test_upload_rejects_wrong_content_type_oversize_and_malformed_before_database():
    client = TestClient(app)
    assert client.post('/api/documents', content=b'hello', headers={'Content-Type': 'text/plain'}).status_code == 415
    assert client.post('/api/documents', content=b'x' * (10 * 1024 * 1024 + 1),
                       headers={'Content-Type': 'application/pdf'}).status_code == 413
    assert client.post('/api/documents', content=b'%PDF-broken',
                       headers={'Content-Type': 'application/pdf'}).status_code == 422


def test_patch_rejects_unknown_fields_invalid_date_accessory_and_status():
    client = TestClient(app)
    for changes in ({'unknown': 'value'}, {'start_date': '2026-02-31'},
                    {'lug_nuts': 'maybe'}, {'action': 'auto_charge'}):
        response = client.patch('/api/documents/00000000-0000-0000-0000-000000000000',
                                json={'version': 1, 'fields': changes, 'status': 'reviewed'})
        assert response.status_code == 422


def test_contact_is_customer_header_only_not_warranty_hotline():
    fields, warnings = parse('Invoice\nBill To Smith, Jane\nCell (555) 010-1111\n'
                            'Inspection\nService\nWarranty hotline (800) 555-9999\n')
    assert '(555) 010-1111' in fields['contact']
    assert '800' not in fields['contact']
    assert 'physical check-in' not in ' '.join(warnings)


def test_other_storage_service_heading_keeps_evidence_and_does_not_become_purchase_only():
    for heading in ('Tire Storage', 'Winter Tire Storage', 'Wheel Storage'):
        fields, warnings = parse('Invoice\nMount, Install & Balance 4 Tires\nNew tire details\n'
                                + heading + '\nNotes__Winter tires 225/60R18\nStorage $99.99\n')
        assert fields['action'] in ('storage', 'review_required')
        assert '225/60R18' in fields['storage_description']


def test_historical_storage_since_is_renewal_candidate_and_wrapped_request_is_kept():
    fields, warnings = parse('Seasonal Tire Storage - Porsche Wheel & Tire Storage since 4/30/2024\nStorage $399.96')
    assert fields['action'] == 'renewal'
    assert any('histor' in warning.lower() for warning in warnings)
    fields, _ = parse('Mount & Balance Tire - Install Tires From Storage / Discard Summers - Make Sure Porsche Center Caps\n'
                      'Face Valve Stem\nMount and balance tire 35 series or less.\nLabor $111.96')
    assert 'Face Valve Stem' in fields['notes']
