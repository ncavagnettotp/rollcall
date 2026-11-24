"""Conservative extraction of digital Protractor document evidence, not events."""
from datetime import date, datetime
import io
import re
from zoneinfo import ZoneInfo

from pypdf import PdfReader

FIELD_KEYS = ('document_type', 'invoice_number', 'work_order_number', 'customer_name',
              'contact', 'vehicle', 'vin', 'start_date', 'date_source',
              'storage_description', 'notes', 'action', 'centering_rings',
              'lug_nuts', 'center_caps')
ACTIONS = {'review_required', 'storage', 'swap', 'retrieval', 'renewal', 'purchase_only'}
MAX_TEXT = 1_000_000


class InvalidPDF(ValueError):
    pass


def parse_text(text: str, today: date | None = None) -> tuple[dict, list[str]]:
    fields = dict.fromkeys(FIELD_KEYS, '')
    fields.update(action='review_required', centering_rings='unknown',
                  lug_nuts='unknown', center_caps='unknown')
    warnings = ['Preliminary suggestion only. Review source details and the proposed start date before later storage actions.']
    # An Invoice heading is evidence of type; payment/authorization boilerplate is not.
    first = next((line.strip().lower() for line in text.splitlines() if line.strip()), '')
    fields['document_type'] = ('invoice' if first == 'invoice' else
                               'authorization' if first == 'authorization' else
                               'work_order' if first in ('work order', 'work-order') else 'unknown')
    for key, pattern in (
        ('invoice_number', r'\bInvoice\s*#\s*(\d+)'),
        ('work_order_number', r'\bWork Order\s*#\s*(\d+)'),
        ('vin', r'\bVIN\s+([A-HJ-NPR-Z0-9]{17})\b'),
    ):
        values = list(dict.fromkeys(re.findall(pattern, text, re.I)))
        if len(values) == 1:
            fields[key] = values[0].upper()
        elif len(values) > 1:
            warnings.append(f'Conflicting {key.replace("_", " ")} values; select the correct value.')
    for key, label in (('customer_name', 'Bill To'), ('vehicle', 'Description')):
        match = re.search(r'\b' + label + r'[ \t]+(.+?)(?:[ \t]{2,}|\n|$)', text, re.I)
        if match:
            fields[key] = match.group(1).strip()
    header = re.split(r'^\s*(?:Inspection|Service)\s*$', text, maxsplit=1, flags=re.I | re.M)[0]
    contacts = re.findall(r'\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', header)
    fields['contact'] = ' · '.join(dict.fromkeys(contacts))

    # Only labeled source dates qualify; footer, appointment and historical dates do not.
    for label in ('Invoice Date', 'Authorization Date', 'Work Order Date'):
        found = re.findall(r'\b' + label + r'[ \t:]+(\d{1,2}/\d{1,2}/\d{4})', text, re.I)
        if not found:
            continue
        if len(set(found)) != 1:
            warnings.append(f'Conflicting {label} values; date requires review.')
            break
        try:
            fields['start_date'] = datetime.strptime(found[0], '%m/%d/%Y').date().isoformat()
            fields['date_source'] = label
        except ValueError:
            warnings.append(f'Invalid {label}; date requires review.')
        break
    if not fields['start_date']:
        fields['start_date'] = (today or datetime.now(ZoneInfo('America/Chicago')).date()).isoformat()
        fields['date_source'] = 'Current shop date (fallback)'
        warnings.append('No reliable labeled source date found; current shop date is a visible fallback and must be checked.')

    storage_match = re.search(r'^\s*(?:(?:Seasonal|Winter|Summer)\s+)?(?:Tire(?:\s*(?:&|and)\s*Wheel)?|Wheel) Storage\b([^\n]*)\n?', text, re.I | re.M)
    package = ''
    if storage_match:
        package = storage_match.group(1) + '\n' + text[storage_match.end():]
        # End at a following real service heading; do not end at a page footer.
        package = re.split(r'^\s*(?:TPMS Sensor|Mount, Install|Alignment Inspection|Lifetime Alignment|Total Parts|Tire Protection Plan)\b', package, maxsplit=1, flags=re.I | re.M)[0]
        operational = re.split(r'Customer acknowledges|Customer is solely|I hereby authorize', package, maxsplit=1, flags=re.I)[0]
        lines = []
        for line in operational.splitlines():
            line = line.strip()
            if not line or re.search(r'Page \d+ of|Store customers|^Storage\s*\$|^Sub\s|^Discount\s', line, re.I):
                continue
            # Remove untouched/selected accessory templates, preserving any Notes tail.
            line = re.sub(r'(?:Lugs|Center caps|Center rings)\s+[YN](?:\s*/\s*[YN])?', '', line, flags=re.I)
            line = re.sub(r'^\s*Notes?[_ :]*', '', line, flags=re.I).strip()
            if line:
                lines.append(line)
        fields['storage_description'] = '\n'.join(lines)[:10000]
        for key, label in (('lug_nuts', 'Lugs'), ('center_caps', 'Center caps'), ('centering_rings', 'Center rings')):
            choices = re.findall(r'\b' + label + r'\s+([YN])\b(\s*/\s*[YN]\b)?', package, re.I)
            values = {value.upper() for value, unselected in choices if not unselected}
            if len(values) == 1:
                fields[key] = 'yes' if next(iter(values)) == 'Y' else 'no'
            elif len(values) > 1:
                warnings.append(f'Conflicting {label.lower()} choices; review accessories.')
    if re.search(r'\bpick\s*up\b|\bfrom storage\b', package if storage_match else text, re.I):
        fields['action'] = 'retrieval'
    elif storage_match and re.search(r'\brenew|(?:stored|storage)\s+since|Winter\s+20\d\d|Summer\s+20\d\d', package, re.I):
        fields['action'] = 'renewal'
        warnings.append('Historical seasons/charges do not determine period boundaries; confirm renewal against history.')
    elif storage_match:
        fields['action'] = 'swap' if re.search(r'^\s*Seasonal Tire Rotation\b', text, re.I | re.M) else 'storage'
    elif re.search(r'^\s*(?:Tire\s*&\s*Wheel Package|Wheels\b|Mount, Install & Balance)', text, re.I | re.M):
        fields['action'] = 'purchase_only'
    # Preserve source-specific notes, not generic legal/payment paragraphs.
    notes = []
    source_lines = text.splitlines()
    for index, line in enumerate(source_lines):
        if re.search(r'Notes[_ :]|NEEDS TIRES REPLACED|center.cap.*(?:align|position)|discard summers|dispose continentals', line, re.I):
            note = re.sub(r'^.*?Notes[_ :]+', '', line, flags=re.I).strip()
            if note:
                notes.append(note)
                for continuation in source_lines[index + 1:index + 4]:
                    continuation = continuation.strip()
                    if not continuation or re.search(r'^(?:Labor|Sub\b|Storage\b|Mount and balance|Includes\b|Customer\b|Store customers|All aluminum|\d{1,2}/)|\$\d', continuation, re.I):
                        break
                    notes.append(continuation)
    fields['notes'] = '\n'.join(dict.fromkeys(notes))[:10000]
    if not fields['vin']:
        warnings.append('VIN missing or ambiguous; select a known vehicle/set later rather than guessing.')
    if fields['document_type'] != 'invoice':
        warnings.append('Pre-invoice document: final invoice must be linked/reconciled in a later storage-action stage.')
    if not text.strip():
        warnings.append('No readable embedded text. Review the original PDF manually; OCR is not supported.')
    return fields, warnings


def extract_pdf(content: bytes) -> tuple[dict, list[str], int, str]:
    if not content.startswith(b'%PDF-'):
        raise InvalidPDF('Upload a valid PDF file.')
    try:
        reader = PdfReader(io.BytesIO(content), strict=False)
        if reader.is_encrypted:
            raise InvalidPDF('Encrypted PDFs are not supported. Export an unencrypted PDF.')
        pages = len(reader.pages)
        if not 1 <= pages <= 50:
            raise InvalidPDF('PDF must contain between 1 and 50 pages.')
        pieces = []
        size = 0
        for page in reader.pages:
            text = page.extract_text(extraction_mode='layout') or ''
            size += len(text)
            if size > MAX_TEXT:
                raise InvalidPDF('PDF text is too large to review safely.')
            pieces.append(text)
        text = '\n'.join(pieces)
        fields, warnings = parse_text(text)
        return fields, warnings, pages, text
    except InvalidPDF:
        raise
    except Exception:
        raise InvalidPDF('PDF could not be read. Export a valid digital PDF and retry.') from None
