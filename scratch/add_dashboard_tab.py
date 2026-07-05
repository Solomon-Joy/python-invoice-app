import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
if "import matplotlib.pyplot as plt" not in content:
    content = content.replace("from database import DatabaseManager, migrate_from_json", "from database import DatabaseManager, migrate_from_json\nimport matplotlib.pyplot as plt\nfrom matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas\nfrom matplotlib.figure import Figure\nfrom collections import defaultdict")

# 2. Add Dashboard to initUI tabs
old_init_tabs = """        self.tabs.addTab(self.gstTab, "GST Invoice")"""
new_init_tabs = """        self.dashboardTab = self.createDashboardTab()
        self.tabs.addTab(self.dashboardTab, "Dashboard")
        self.tabs.addTab(self.gstTab, "GST Invoice")"""
if "self.dashboardTab =" not in content:
    content = content.replace(old_init_tabs, new_init_tabs)

# 3. Add createDashboardTab function
dashboard_func = """    def createDashboardTab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Top Stats
        statsLayout = QHBoxLayout()
        self.lblTotalRevenue = QLabel("Total Revenue: Rs. 0.00")
        self.lblTotalInvoices = QLabel("Total Invoices: 0")
        self.lblTotalRevenue.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.lblTotalInvoices.setStyleSheet("font-size: 16px; font-weight: bold;")
        statsLayout.addWidget(self.lblTotalRevenue)
        statsLayout.addWidget(self.lblTotalInvoices)
        layout.addLayout(statsLayout)

        # Chart
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        btnRefresh = QPushButton("Refresh Dashboard")
        btnRefresh.clicked.connect(self.updateDashboard)
        layout.addWidget(btnRefresh)

        return widget

    def updateDashboard(self):
        if not hasattr(self, 'dashboardTab'):
            return
            
        invoices = self.db.get_all_invoices()
        total_rev = sum(inv.get('netPayable', 0.0) for inv in invoices)
        self.lblTotalRevenue.setText(f"Total Revenue: Rs. {total_rev:,.2f}")
        self.lblTotalInvoices.setText(f"Total Invoices: {len(invoices)}")
        
        # Group by date for chart
        revenue_by_date = defaultdict(float)
        for inv in invoices:
            date_str = inv.get('date', '')
            if date_str:
                revenue_by_date[date_str] += inv.get('netPayable', 0.0)
                
        sorted_dates = sorted(revenue_by_date.keys())
        revenues = [revenue_by_date[d] for d in sorted_dates]
        
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if sorted_dates:
            ax.bar(sorted_dates, revenues, color='#3498db')
            ax.set_title("Revenue Over Time")
            ax.set_ylabel("Revenue (Rs.)")
            ax.tick_params(axis='x', rotation=45)
            self.figure.tight_layout()
        else:
            ax.text(0.5, 0.5, "No Data Available", ha='center', va='center')
        
        self.canvas.draw()

"""

# Insert before createHistoryTab
target = "    def createHistoryTab(self):"
if dashboard_func not in content:
    content = content.replace(target, dashboard_func + target)

# 4. Call updateDashboard after init
init_end = "self.invoiceIndex = self.db.get_all_invoices()"
new_init_end = "self.invoiceIndex = self.db.get_all_invoices()\n        self.updateDashboard()"
if "self.updateDashboard()" not in content:
    content = content.replace(init_end, new_init_end)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
