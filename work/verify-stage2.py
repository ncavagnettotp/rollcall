"""Manual local Stage 2 acceptance against the running API; no storage events."""
from pathlib import Path
from io import BytesIO
import hashlib
import json
import urllib.request
import urllib.error
import urllib.parse
from pypdf import PdfWriter

BASE = 'http://127.0.0.1:8000'
SOURCE = Path('C:/Users/ndcav/OneDrive/Desktop/Storage Examples')

def request(path, data=None, method=None, headers=None):
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            body = response.read()
            return response.status, json.loads(body) if response.headers.get_content_type() == 'application/json' else body
    except urllib.error.HTTPError as error:
        return error.code, json.loads(error.read())

expected = {
    '246537': ('', 'swap'), '213906': ('2026-08-24', 'purchase_only'),
    '215885': ('2026-10-26', 'purchase_only'), '210874': ('2026-05-18', 'retrieval'),
    '210893': ('2026-05-19', None), '210794': ('2026-05-15', None),
    '215798': ('2026-10-22', 'swap'), '215777': ('2026-10-22', 'retrieval'),
}
results = []
for file in sorted(SOURCE.glob('*.pdf')):
    content = file.read_bytes()
    headers = {'Content-Type':'application/pdf','X-Filename':urllib.parse.quote(file.name)}
    status, doc = request('/api/documents', content, headers=headers)
    assert status in (200,201), (file.name, status, doc)
    fields = doc['extracted']
    number = fields['invoice_number'] or fields['work_order_number']
    date, action = expected[number]
    if date: assert fields['start_date'] == date, (number,'date',fields['start_date'])
    if action: assert fields['action'] == action, (number,'action',fields['action'])
    if number == '215798':
        assert [fields[k] for k in ['lug_nuts','center_caps','centering_rings']] == ['yes','yes','no']
        assert 'NEEDS TIRES REPLACED' in fields['notes'] or 'NEEDS TIRES REPLACED' in fields['storage_description']
    if number == '210893':
        assert '275/35R21' in fields['storage_description'] and '315/30R21' in fields['storage_description']
        assert fields['lug_nuts'] == 'unknown'
    status, duplicate = request('/api/documents',content,headers=headers)
    assert status in (200,201) and duplicate['id'] == doc['id'] and duplicate['duplicate'] is True
    status, original = request(doc['pdf_url'])
    assert status == 200 and hashlib.sha256(original).digest() == hashlib.sha256(content).digest()
    results.append({'document_id':number,'pages':doc['pages'],'action':fields['action'],'original_and_duplicate':'PASS'})
    print('PASS:', number, 'fields, original bytes, duplicate reopen')

buffer = BytesIO()
writer = PdfWriter()
writer.add_blank_page(width=612,height=792)
writer.write(buffer)
status, probe = request('/api/documents',buffer.getvalue(),headers={'Content-Type':'application/pdf','X-Filename':'stage2-verification-blank.pdf'})
assert status in (200,201) and probe['warnings']
original_fields = dict(probe['extracted'])
fields = dict(probe['fields'])
fields['notes'] = 'Stage 2 verification: saved correction survives reload.'
payload = {'version':probe['version'],'fields':fields,'status':'reviewed'}
status, saved = request('/api/documents/'+probe['id'],json.dumps(payload).encode(),method='PATCH',headers={'Content-Type':'application/json'})
assert status == 200 and saved['version'] == probe['version'] + 1
assert saved['extracted'] == original_fields and saved['fields']['notes'] == fields['notes']
assert request('/api/documents/'+probe['id'],json.dumps(payload).encode(),method='PATCH',headers={'Content-Type':'application/json'})[0] == 409
status, reopened = request('/api/documents/'+probe['id'])
assert status == 200 and reopened['fields']['notes'] == fields['notes']
assert request('/api/documents',b'not a PDF',headers={'Content-Type':'application/pdf'})[0] in (400,422)
status, listing = request('/api/documents')
assert status == 200 and len(listing['documents']) >= 9
output = Path('docs/verification/2026-11-10-stage2-api.json')
output.write_text(json.dumps({'samples':results,'checks':['8 real PDFs','exact original retrieval','duplicate SHA256','no-text warning','review persistence','immutable extraction','stale revision 409','malformed rejection','list/reopen'],'result':'PASS'},indent=2),encoding='utf-8')
print('PASS: no-text/manual review, saved corrections, immutable extraction, conflict protection, malformed rejection, list/reopen')
