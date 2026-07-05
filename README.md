# Invoice Writer — Python + PyQt5

A lightweight desktop application for creating GST and Standard invoices with PDF export, customer/product profiles, and invoice history. Built with PyQt5 and ReportLab for fast, offline-friendly billing workflows.

## Features
- GST and Standard invoice workflows with multi-tab UI
- Automatic GST calculations (CGST/SGST), round-off, and net payable
- Professional PDF generation with multi-copy GST output
- Customer and product profile management (JSON persistence)
- Invoice history with search, reprint, and CSV export
- CSV export and optional Excel export (openpyxl)

## Tech Stack
- Python 3.7+
- PyQt5 (desktop UI)
- ReportLab (PDF generation)
- OpenPyXL (optional Excel export)

## Project Structure
- `app.py` — Main application
- `data/` — Local JSON storage (customers, products, invoice index)
- `requirements.txt` — Python dependencies

## Setup
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run
```bash
python app.py
```

## Notes
- Excel export requires `openpyxl` (already in `requirements.txt` if needed).
- All data is stored locally under `data/`.

## Screenshots
Add screenshots here if you want:
- `docs/screenshot-1.png`
- `docs/screenshot-2.png`

## License
MIT (or choose a license of your choice)
