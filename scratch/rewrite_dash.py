import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update createDashboardTab
old_create = """    def createDashboardTab(self):
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure
        
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

        return widget"""

new_create = """    def createDashboardTab(self):
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
        self.chartLabel = QLabel()
        from PyQt5.QtCore import Qt
        self.chartLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.chartLabel)

        btnRefresh = QPushButton("Refresh Dashboard")
        btnRefresh.clicked.connect(self.updateDashboard)
        layout.addWidget(btnRefresh)

        return widget"""

content = content.replace(old_create, new_create)

# 2. Update updateDashboard
old_update = """    def updateDashboard(self):
        from collections import defaultdict
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
        
        self.canvas.draw()"""

new_update = """    def updateDashboard(self):
        from collections import defaultdict
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from PyQt5.QtGui import QPixmap
        
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
        
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100)
        if sorted_dates:
            ax.bar(sorted_dates, revenues, color='#3498db')
            ax.set_title("Revenue Over Time")
            ax.set_ylabel("Revenue (Rs.)")
            ax.tick_params(axis='x', rotation=45)
            fig.tight_layout()
        else:
            ax.text(0.5, 0.5, "No Data Available", ha='center', va='center')
            
        chart_path = str(self.dataDir / "chart.png")
        fig.savefig(chart_path)
        plt.close(fig)
        
        pixmap = QPixmap(chart_path)
        self.chartLabel.setPixmap(pixmap)"""

content = content.replace(old_update, new_update)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
