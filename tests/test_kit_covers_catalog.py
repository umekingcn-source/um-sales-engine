"""
Smoke tests: kit-covers 01–24 files and catalog PDF generation with covers.
Run from repo root: python tests/test_kit_covers_catalog.py
"""
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE)

import data_manager as dm
import pdf_generator as pdfgen


def test_kit_cover_files():
    folder = os.path.join(BASE, "assets", "images", "kit-covers")
    assert os.path.isdir(folder), f"Missing folder: {folder}"
    missing = []
    for i in range(1, 25):
        stem = os.path.join(folder, f"{i:02d}")
        found = any(os.path.isfile(stem + ext) for ext in pdfgen.KIT_COVER_EXTENSIONS)
        if not found:
            missing.append(f"{i:02d}")
    assert not missing, f"Missing kit cover files for: {', '.join(missing)}"


def test_kit_cover_path_resolution():
    for cat in dm.PRESET_CATEGORIES:
        p = pdfgen.get_kit_cover_absolute_path(cat)
        assert p and os.path.isfile(p), f"No cover resolved for: {cat[:50]}..."


def test_catalog_pdf_with_covers():
    df = dm.get_products_df()
    assert len(df) > 0, "Need at least one product in products.csv"
    settings = dm.get_settings()
    products = []
    for _, row in df.head(12).iterrows():
        products.append(row.to_dict())
    buf = pdfgen.generate_catalog_pdf(
        products=products,
        settings=settings,
        catalog_number="TEST-KIT-COVER-001",
        catalog_date="May 12, 2026",
        language="English",
    )
    data = buf.getvalue()
    assert len(data) > 2000, "PDF buffer unexpectedly small"
    assert data[:4] == b"%PDF", "Not a valid PDF header"


if __name__ == "__main__":
    test_kit_cover_files()
    print("OK: kit-covers 01–24 files exist")
    test_kit_cover_path_resolution()
    print("OK: get_kit_cover_absolute_path for all PRESET_CATEGORIES")
    test_catalog_pdf_with_covers()
    print("OK: catalog PDF generated with kit banners")
    df = dm.get_products_df()
    out = os.path.join(BASE, "tests", "_catalog_kit_cover_smoke.pdf")
    buf = pdfgen.generate_catalog_pdf(
        products=[df.iloc[i].to_dict() for i in range(min(5, len(df)))],
        settings=dm.get_settings(),
        catalog_number="SMOKE",
        catalog_date="May 12, 2026",
        language="English",
    )
    data = buf.getvalue()
    with open(out, "wb") as f:
        f.write(data)
    print(f"Wrote sample PDF: {out} ({len(data)} bytes)")
