"""Write the synthetic sample invoice shown beside the tire set form in the mockup gallery.

Run: uv run python scripts/make_sample_invoice.py

The PDF is laid out like a Protractor invoice (the labels the PDF pre-fill reads, see
openspec/changes/plan-rollcall-rewrite/v1-lessons.md) but every name, number and address in it
is invented. Phone numbers use the fictional 555-01xx range, the email uses example.com and the
VIN spells EXAMPLE. Never copy anything from a real invoice into this file.

The PDF is written by hand, with no library, and the output is the same on every run, so
tests/test_mockups.py can check that the committed file is exactly what this script makes.
"""

from pathlib import Path

OUTPUT = Path(__file__).parent.parent / "rollcall" / "mockups" / "sample-invoice.pdf"

PAGE_WIDTH, PAGE_HEIGHT = 612, 792  # US letter, in points
LEFT, RIGHT = 48, 564

# (x, y, font size, bold?, text). y counts up from the bottom of the page.
TEXT = [
    (LEFT, 748, 20, True, "Invoice"),
    (360, 744, 11, True, "Lakeview Tire & Auto"),
    (360, 730, 9, False, "4410 Example Parkway"),
    (360, 718, 9, False, "Springfield, IL 62700"),
    (360, 706, 9, False, "(555) 010-4400"),
    # header
    (LEFT, 670, 10, True, "Bill To"),
    (110, 670, 10, False, "Kowalczyk, Renata"),
    (110, 656, 10, False, "(555) 014-2271"),
    (110, 642, 10, False, "renata.k@example.com"),
    (360, 670, 10, True, "Invoice #"),
    (450, 670, 10, False, "900123"),
    (360, 656, 10, True, "Work Order #"),
    (450, 656, 10, False, "48213"),
    (360, 642, 10, True, "Invoice Date"),
    (450, 642, 10, False, "11/18/2026"),
    (LEFT, 612, 10, True, "Description"),
    (130, 612, 10, False, "2019 Subaru Outback"),
    (LEFT, 598, 10, True, "VIN"),
    (130, 598, 10, False, "JF2EXAMPLE0000001"),
    (LEFT, 584, 10, True, "License"),
    (130, 584, 10, False, "IL SMPL 123"),
    (360, 598, 10, True, "Odometer"),
    (450, 598, 10, False, "61,204"),
    # services
    (LEFT, 548, 11, True, "Mount, Install"),
    (LEFT, 534, 9, False, "Mount and balance 4 winter tires on steel wheels."),
    (500, 548, 10, False, "$119.96"),
    (LEFT, 508, 11, True, "Seasonal Tire Storage"),
    (LEFT, 494, 9, False, "Store customers wheels/tires. 6 month maximum."),
    (
        LEFT,
        480,
        9,
        False,
        "Lugs Y  Center caps Y / N  Center rings N  "
        "Notes__225/60R17 Bridgestone Alenza on OEM alloys",
    ),
    (500, 508, 10, False, "$99.99"),
    (LEFT, 454, 11, True, "TPMS Sensor"),
    (LEFT, 440, 9, False, "Inspect and relearn 4 sensors."),
    (500, 454, 10, False, "$24.00"),
    # totals
    (360, 400, 10, False, "Total Parts"),
    (500, 400, 10, False, "$0.00"),
    (360, 386, 10, False, "Total Labor"),
    (500, 386, 10, False, "$243.95"),
    (360, 368, 11, True, "Total"),
    (500, 368, 11, True, "$243.95"),
    (
        LEFT,
        320,
        8,
        False,
        "Customer acknowledges that stored tires are held for six months at most.",
    ),
    (LEFT, 96, 8, True, "SAMPLE INVOICE: every name, number and address on it is invented."),
    (LEFT, 48, 8, False, "11/18/2026 4:12 PM Invoice #900123 Page 1 of 1"),
]

# Horizontal rules: (y, line width)
RULES = [(694, 1.0), (568, 0.5), (420, 0.5), (60, 0.5)]


def lines_text() -> list[str]:
    """The invoice's text, top to bottom, one line per row (as text extraction reads it)."""
    rows: dict[int, list[tuple[int, str]]] = {}
    for x, y, _size, _bold, text in TEXT:
        rows.setdefault(y, []).append((x, text))
    return [" ".join(t for _, t in sorted(rows[y])) for y in sorted(rows, reverse=True)]


def _escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _content() -> bytes:
    lines = [f"{width} w {LEFT} {y} m {RIGHT} {y} l S" for y, width in RULES]
    for x, y, size, bold, text in TEXT:
        font = "F2" if bold else "F1"
        lines.append(f"BT /{font} {size} Tf {x} {y} Td ({_escape(text)}) Tj ET")
    return "\n".join(lines).encode("latin-1")


def build() -> bytes:
    """The whole PDF file."""
    content = _content()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            "/Resources << /Font << /F1 4 0 R /F2 5 0 R >> >> /Contents 6 0 R >>"
        ).encode(),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>",
        b"<< /Length %d >>\nstream\n" % len(content) + content + b"\nendstream",
        b"<< /Title (Sample invoice) /Producer (Rollcall make_sample_invoice.py) >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for number, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + body + b"\nendobj\n"
    xref_at = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += b"trailer\n<< /Size %d /Root 1 0 R /Info 7 0 R >>\n" % (len(objects) + 1)
    out += b"startxref\n%d\n%%%%EOF\n" % xref_at
    return bytes(out)


if __name__ == "__main__":
    OUTPUT.write_bytes(build())
    print(f"Wrote {OUTPUT}")
