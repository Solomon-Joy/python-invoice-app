import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
if "from database import DatabaseManager" not in content:
    content = content.replace("import urllib.parse", "import urllib.parse\nfrom database import DatabaseManager, migrate_from_json")

# 2. InitDB block
old_init = """        self.customersFile = self.dataDir / "customers.json"
        self.productsFile = self.dataDir / "products.json"
        self.countersFile = self.dataDir / "counters.json"
        self.indexFile = self.dataDir / "invoice_index.json"

        self.customers = self.loadJson(self.customersFile, [])
        self.products = self.loadJson(self.productsFile, [])
        self.counters = self.loadJson(self.countersFile, {})
        self.invoiceIndex = self.loadJson(self.indexFile, [])"""

new_init = """        db_path = self.dataDir / "invoice_app.db"
        self.db = DatabaseManager(db_path)
        
        migration_flag = self.dataDir / ".migrated"
        if not migration_flag.exists():
            migrate_from_json(self.dataDir, self.db)
            migration_flag.touch()

        self.customers = self.db.get_all_customers()
        self.products = self.db.get_all_products()
        self.counters = self.db.get_setting('counters', {})
        self.invoiceIndex = self.db.get_all_invoices()"""

content = content.replace(old_init, new_init)

# 3. Save calls
# Customers
content = content.replace("self.saveJson(self.customersFile, self.customers)", "self.db.add_or_update_customer(customer)\n        self.customers = self.db.get_all_customers()")
# Products
content = content.replace("self.saveJson(self.productsFile, self.products)", "self.db.add_or_update_product(product)\n        self.products = self.db.get_all_products()")
# Counters
content = content.replace("self.saveJson(self.countersFile, self.counters)", "self.db.set_setting('counters', self.counters)")
# Invoice Index
content = content.replace("self.saveJson(self.indexFile, self.invoiceIndex)", "self.db.add_invoice_index(payload)\n            self.invoiceIndex = self.db.get_all_invoices()")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
