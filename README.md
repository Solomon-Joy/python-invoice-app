# 🧾 Python Invoice App

A professional, lightweight, and offline-first desktop billing application designed for businesses that need to generate beautiful GST and standard invoices quickly. Built entirely with **Python**, **PyQt5**, and **ReportLab**.

This application is designed specifically to mirror traditional physical bill books, offering 13-column GST layouts with automatic tax calculations, local JSON storage for customer/product data, and robust PDF/CSV exporting capabilities.

---

## 🌟 Key Features

### 🏢 Comprehensive Billing Workflows
- **GST & Standard Invoicing:** Dedicated tabs for different billing needs.
- **Physical Bill Replica:** PDF output is precisely formatted to perfectly replicate a traditional manual GST bill book.
- **13-Column Detail:** Built-in support for HSN/SAC, MRP, Discount %, and Taxable Value tracking.
- **Automatic Calculations:** Line-by-line automatic generation of Subtotals, CGST/SGST amounts (based on dynamic rates), net payable, and automated round-off.
- **Multi-Copy Output:** One-click generation of multiple invoice copies (e.g., Original for Buyer, Duplicate for Transporter, Triplicate for Supplier).

### 👥 Customer & Product Management
- **Customer Profiles:** Save regular vendors/customers and autocomplete their details (Address, GSTIN, Contact).
- **Product Database:** Maintain a local inventory with predefined HSN codes, default MRPs, and unit prices for quick 1-click additions to bills.
- **100% Offline Storage:** All data is securely persisted locally using JSON files.

### 📊 History & Exporting
- **Invoice Dashboard:** View a complete history of all generated invoices.
- **Search & Filter:** Instantly filter past invoices by Customer Name, Invoice Number, or Date.
- **CSV/Excel Export:** Generate comprehensive Excel (via OpenPyXL) or CSV reports for accounting software imports.
- **Reprinting:** One-click reprint of old PDF invoices directly from the dashboard.

---

## 🛠️ Tech Stack

- **[Python 3.7+](https://www.python.org/):** Core application logic.
- **[PyQt5](https://pypi.org/project/PyQt5/):** Fast, native-feeling graphical user interface (GUI).
- **[ReportLab](https://pypi.org/project/reportlab/):** Programmatic, highly customizable PDF generation.
- **[OpenPyXL](https://pypi.org/project/openpyxl/):** Optional Excel export capabilities.

---

## 📁 Project Structure

```text
python-invoice-app/
├── app.py               # Main application and GUI logic
├── requirements.txt     # Python dependencies
├── README.md            # You are here
└── data/                # Auto-generated directory for local storage
    ├── customers.json   # Saved customer profiles
    ├── products.json    # Saved product catalog
    └── history.json     # Ledger of all past invoices
```

---

## 🚀 Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/python-invoice-app.git
   cd python-invoice-app
   ```

2. **Create a Virtual Environment (Recommended)**
   ```bash
   python -m venv .venv
   
   # Activate on Windows:
   .\.venv\Scripts\activate
   
   # Activate on macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the App!**
   ```bash
   python app.py
   ```

---

## 📖 Usage Guide

1. **Creating an Invoice:** Navigate to the `GST Invoice` or `Normal Invoice` tab. Fill out vendor details (or select from saved customers) and add items.
2. **Preview & Print:** Click `Preview & Print` to generate the PDF and automatically open it in your default PDF viewer.
3. **Saving Data:** Any customer or product added manually can be saved for future use by clicking the respective `Save Customer` or `Save Product` buttons in their management tabs.
4. **Viewing History:** Go to the `Invoice History` tab to view past transactions, export the ledger to `.xlsx`, or reprint old PDFs.

---

## 📸 Screenshots

*(You can replace these links with actual screenshots of your application in a `docs/` folder)*
- `docs/gst-invoice-tab.png`
- `docs/invoice-history.png`
- `docs/sample-pdf.png`

---

## 📄 License

This project is open-sourced under the MIT License. Feel free to modify and adapt it for your own business needs!
