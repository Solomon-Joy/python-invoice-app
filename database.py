import sqlite3
import json
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Settings Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            # Customers Table (using app.py keys)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    vendorName TEXT PRIMARY KEY,
                    vendorGST TEXT,
                    vendorContact TEXT,
                    vendorAddress TEXT,
                    vendorState TEXT,
                    vendorPin TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Products Table (using app.py keys)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    name TEXT PRIMARY KEY,
                    hsn TEXT,
                    unit TEXT,
                    price REAL,
                    mrp REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Invoices Table (using app.py keys)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    invoiceNumber TEXT PRIMARY KEY,
                    date TEXT,
                    vendorName TEXT,
                    netPayable REAL,
                    pdfPath TEXT,
                    jsonPath TEXT,
                    type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    # Settings CRUD
    def get_setting(self, key, default=None):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            row = cursor.fetchone()
            return json.loads(row['value']) if row else default

    def set_setting(self, key, value):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO settings (key, value) VALUES (?, ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
            ''', (key, json.dumps(value)))
            conn.commit()

    # Customers CRUD
    def add_or_update_customer(self, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO customers (vendorName, vendorGST, vendorContact, vendorAddress, vendorState, vendorPin)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(vendorName) DO UPDATE SET
                    vendorGST = excluded.vendorGST,
                    vendorContact = excluded.vendorContact,
                    vendorAddress = excluded.vendorAddress,
                    vendorState = excluded.vendorState,
                    vendorPin = excluded.vendorPin
            ''', (
                data.get('vendorName'),
                data.get('vendorGST'),
                data.get('vendorContact'),
                data.get('vendorAddress'),
                data.get('vendorState'),
                data.get('vendorPin')
            ))
            conn.commit()

    def get_all_customers(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM customers ORDER BY vendorName')
            return [dict(row) for row in cursor.fetchall()]

    # Products CRUD
    def add_or_update_product(self, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO products (name, hsn, unit, price, mrp)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    hsn = excluded.hsn,
                    unit = excluded.unit,
                    price = excluded.price,
                    mrp = excluded.mrp
            ''', (
                data.get('name'),
                data.get('hsn'),
                data.get('unit'),
                data.get('price', 0.0),
                data.get('mrp', 0.0)
            ))
            conn.commit()

    def get_all_products(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products ORDER BY name')
            return [dict(row) for row in cursor.fetchall()]

    # Invoices CRUD
    def add_invoice_index(self, data):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO invoices (invoiceNumber, date, vendorName, netPayable, pdfPath, jsonPath, type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(invoiceNumber) DO UPDATE SET
                    date = excluded.date,
                    vendorName = excluded.vendorName,
                    netPayable = excluded.netPayable,
                    pdfPath = excluded.pdfPath,
                    jsonPath = excluded.jsonPath,
                    type = excluded.type
            ''', (
                data.get('invoiceNumber'),
                data.get('date'),
                data.get('vendorName'),
                data.get('netPayable'),
                data.get('pdfPath'),
                data.get('jsonPath'),
                data.get('type')
            ))
            conn.commit()

    def get_all_invoices(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM invoices ORDER BY created_at DESC')
            return [dict(row) for row in cursor.fetchall()]

def migrate_from_json(data_dir: Path, db: DatabaseManager):
    """One-time migration script from JSON files to SQLite."""
    counters_file = data_dir / "counters.json"
    if counters_file.exists():
        with open(counters_file, 'r', encoding='utf-8') as f:
            try:
                counters = json.load(f)
                db.set_setting('counters', counters)
                counters_file.rename(counters_file.with_suffix('.json.bak'))
            except Exception:
                pass
        
    customers_file = data_dir / "customers.json"
    if customers_file.exists():
        with open(customers_file, 'r', encoding='utf-8') as f:
            try:
                customers = json.load(f)
                for cust in customers:
                    db.add_or_update_customer(cust)
                customers_file.rename(customers_file.with_suffix('.json.bak'))
            except Exception:
                pass

    products_file = data_dir / "products.json"
    if products_file.exists():
        with open(products_file, 'r', encoding='utf-8') as f:
            try:
                products = json.load(f)
                for prod in products:
                    db.add_or_update_product(prod)
                products_file.rename(products_file.with_suffix('.json.bak'))
            except Exception:
                pass

    index_file = data_dir / "invoice_index.json"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            try:
                index = json.load(f)
                for inv in index:
                    db.add_invoice_index(inv)
                index_file.rename(index_file.with_suffix('.json.bak'))
            except Exception:
                pass
