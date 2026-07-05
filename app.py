"""
Invoice Writer - Python + PyQt Demo
A simple, fast desktop application for creating GST and Normal invoices
"""

import sys
import csv
import json
import os
import urllib.parse
import webbrowser
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
    QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox, QHeaderView,
    QScrollArea, QFormLayout, QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

class InvoiceWriter(QMainWindow):
    NORMAL_TAX_RATE = 0.10
    GST_CGST_RATE = 0.025
    GST_SGST_RATE = 0.025
    PDF_CURRENCY = "Rs."
    GST_COPY_LABELS = [
        "ORIGINAL FOR VENDOR",
        "COPY FOR DISTRIBUTOR",
        "OFFICIAL PURPOSE COPY",
    ]
    COMPANY_NAME = "RINA RICH FOOD & AGENCIES"
    COMPANY_ADDRESS = "Aranattukara, Thrissur, Kerala - 680301"
    COMPANY_PHONE = "+91-9895314201"
    COMPANY_GSTIN = "32AZOPR2558K1ZU"
    COMPANY_STATE = "32-Kerala"
    DISTRIBUTOR_EMAIL = "15solomonjoyc12020@gmail.com"
    AUDIT_EMAIL = "15solomonjoyc12020@gmail.com"

    def __init__(self):
        super().__init__()
        self.baseDir = Path(__file__).resolve().parent
        self.dataDir = self.baseDir / "data"
        self.invoicesDir = self.dataDir / "invoices"
        self.dataDir.mkdir(parents=True, exist_ok=True)
        self.invoicesDir.mkdir(parents=True, exist_ok=True)
        self.customersFile = self.dataDir / "customers.json"
        self.productsFile = self.dataDir / "products.json"
        self.countersFile = self.dataDir / "counters.json"
        self.indexFile = self.dataDir / "invoice_index.json"
        self.customers = self.loadJson(self.customersFile, [])
        self.products = self.loadJson(self.productsFile, [])
        self.counters = self.loadJson(self.countersFile, {})
        self.invoiceIndex = self.loadJson(self.indexFile, [])
        self.initUI()
        self.invoiceData = {}

    def initUI(self):
        self.setWindowTitle('Invoice Writer System ')
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget and layout
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        layout = QVBoxLayout(mainWidget)
        self.applyAppStyle()

        # Header
        headerLabel = QLabel('Invoice Writer System')
        headerFont = QFont()
        headerFont.setPointSize(18)
        headerFont.setBold(True)
        headerLabel.setFont(headerFont)
        headerLabel.setProperty("variant", "title")
        layout.addWidget(headerLabel)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.createNormalInvoiceTab(), "Normal Invoice")
        self.tabs.addTab(self.createGSTInvoiceTab(), "GST Invoice")
        self.tabs.addTab(self.createHistoryTab(), "Invoice History")
        layout.addWidget(self.tabs)

    def loadJson(self, path, default):
        if not path.exists():
            return default
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def saveJson(self, path, payload):
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

    def createNormalInvoiceTab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Company Info
        companyGroup = self.createSection("Company Information")
        companyGroup['vendorName'] = self.addInputField(companyGroup['layout'], "Vendor Name *", "Enter customer name")
        companyGroup['vendorAddress'] = self.addTextArea(companyGroup['layout'], "Vendor Address", 3)
        layout.addWidget(companyGroup['widget'])

        # Invoice Details
        invoiceGroup = self.createSection("Invoice Details")
        invoiceGroup['invoiceNumber'] = self.addInputField(invoiceGroup['layout'], "Invoice Number *", "e.g., INV-001")
        invoiceGroup['date'] = self.addDateField(invoiceGroup['layout'], "Date")
        layout.addWidget(invoiceGroup['widget'])

        # Items Table
        itemsGroup = self.createSection("Items")
        self.normalItemsTable = QTableWidget()
        self.normalItemsTable.setColumnCount(5)
        self.normalItemsTable.setHorizontalHeaderLabels(['Description', 'Qty', 'Unit Price', 'Amount', 'Remove'])
        self.setupItemsTable(self.normalItemsTable)
        itemsGroup['layout'].addWidget(self.normalItemsTable)
        
        addItemBtn = QPushButton('+ Add Item')
        addItemBtn.setObjectName("success")
        addItemBtn.clicked.connect(lambda: self.addItemToTable(self.normalItemsTable))
        itemsGroup['layout'].addWidget(addItemBtn)
        layout.addWidget(itemsGroup['widget'])

        # Summary
        summaryGroup = self.createSection("Summary")
        self.normalSubtotal = QLabel("Subtotal: ₹0.00")
        self.normalTax = QLabel(f"Tax ({int(self.NORMAL_TAX_RATE * 100)}%): ₹0.00")
        self.normalTotal = QLabel("Total: ₹0.00")
        summaryFont = QFont()
        summaryFont.setPointSize(11)
        self.normalTotal.setFont(summaryFont)
        self.normalTotal.setProperty("variant", "highlight")
        summaryGroup['layout'].addWidget(self.normalSubtotal)
        summaryGroup['layout'].addWidget(self.normalTax)
        summaryGroup['layout'].addWidget(self.normalTotal)
        layout.addWidget(summaryGroup['widget'])

        # Buttons
        btnLayout = QHBoxLayout()
        previewBtn = QPushButton('Preview & Print')
        previewBtn.setObjectName("primary")
        previewBtn.clicked.connect(lambda: self.previewNormalInvoice(invoiceGroup, companyGroup, itemsGroup))
        btnLayout.addStretch()
        btnLayout.addWidget(previewBtn)
        layout.addLayout(btnLayout)

        layout.addStretch()
        return self.wrapInScrollArea(widget)

    def createGSTInvoiceTab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.gstFields = {}

        # GST Form Subsections
        customerGroup = self.createSection("1) Customer & Billing")
        self.gstCustomerCombo = QComboBox()
        self.gstCustomerCombo.addItem("Select saved customer...")
        self.gstCustomerCombo.currentIndexChanged.connect(self.onCustomerSelected)
        customerGroup['layout'].addWidget(self.gstCustomerCombo)

        form1 = QFormLayout()
        form1.setSpacing(8)
        self.gstFields['vendorName'] = QLineEdit()
        self.gstFields['vendorAddress'] = QTextEdit()
        self.gstFields['vendorAddress'].setMaximumHeight(70)
        self.gstFields['vendorGST'] = QLineEdit()
        self.gstFields['vendorGST'].setMaxLength(15)
        self.gstFields['vendorGST'].setPlaceholderText("15-character GSTIN")
        self.gstFields['vendorContact'] = QLineEdit()
        self.gstFields['vendorContact'].setInputMask("9999999999;_")
        self.gstFields['vendorContact'].setPlaceholderText("10-digit mobile number")
        self.gstFields['vendorState'] = QLineEdit()
        self.gstFields['vendorPin'] = QLineEdit()
        self.gstFields['vendorPin'].setInputMask("999999;_")
        form1.addRow("Vendor Name *", self.gstFields['vendorName'])
        form1.addRow("Vendor Address", self.gstFields['vendorAddress'])
        form1.addRow("Vendor GST Number", self.gstFields['vendorGST'])
        form1.addRow("Vendor Contact", self.gstFields['vendorContact'])
        form1.addRow("Vendor State", self.gstFields['vendorState'])
        form1.addRow("Vendor PIN", self.gstFields['vendorPin'])
        customerGroup['layout'].addLayout(form1)
        saveCustomerBtn = QPushButton("Save Customer Profile")
        saveCustomerBtn.setObjectName("success")
        saveCustomerBtn.clicked.connect(self.saveCurrentCustomer)
        customerGroup['layout'].addWidget(saveCustomerBtn)
        layout.addWidget(customerGroup['widget'])

        supplyGroup = self.createSection("2) Invoice, Tax & Supply")
        form2 = QFormLayout()
        form2.setSpacing(8)
        self.gstFields['invoiceNumber'] = QLineEdit()
        self.gstFields['date'] = QLineEdit(datetime.now().strftime("%d-%m-%Y"))
        self.gstFields['date'].setInputMask("99-99-9999;_")
        self.gstFields['date'].setPlaceholderText("DD-MM-YYYY")
        self.gstFields['placeOfSupply'] = QLineEdit()
        self.gstFields['vehicleNumber'] = QLineEdit()
        self.gstFields['hsnSac'] = QLineEdit("19059010")
        self.gstFields['unitName'] = QLineEdit("Nos")
        self.gstFields['previousBalance'] = QLineEdit("0")
        self.gstFields['advanceReceived'] = QLineEdit("0")
        self.gstFields['roundOff'] = QLineEdit("0")
        form2.addRow("Invoice Number *", self.gstFields['invoiceNumber'])
        autoNoBtn = QPushButton("Auto Generate Number")
        autoNoBtn.setObjectName("secondary")
        autoNoBtn.clicked.connect(self.generateInvoiceNumber)
        form2.addRow("", autoNoBtn)
        form2.addRow("Date", self.gstFields['date'])
        form2.addRow("Place Of Supply", self.gstFields['placeOfSupply'])
        form2.addRow("Vehicle Number", self.gstFields['vehicleNumber'])
        form2.addRow("HSN/SAC", self.gstFields['hsnSac'])
        form2.addRow("Unit", self.gstFields['unitName'])
        form2.addRow("Previous Balance", self.gstFields['previousBalance'])
        form2.addRow("Advance Received", self.gstFields['advanceReceived'])
        form2.addRow("Round Off (+/-)", self.gstFields['roundOff'])
        supplyGroup['layout'].addLayout(form2)

        copiesBox = QGroupBox("3) Copy Selection")
        copiesLayout = QVBoxLayout(copiesBox)
        self.copyVendorCheck = QCheckBox(self.GST_COPY_LABELS[0])
        self.copyDistributorCheck = QCheckBox(self.GST_COPY_LABELS[1])
        self.copyOfficialCheck = QCheckBox(self.GST_COPY_LABELS[2])
        self.copyVendorCheck.setChecked(True)
        self.copyDistributorCheck.setChecked(True)
        self.copyOfficialCheck.setChecked(True)
        copiesLayout.addWidget(self.copyVendorCheck)
        copiesLayout.addWidget(self.copyDistributorCheck)
        copiesLayout.addWidget(self.copyOfficialCheck)
        supplyGroup['layout'].addWidget(copiesBox)
        layout.addWidget(supplyGroup['widget'])

        productGroup = self.createSection("4) Product Defaults")
        self.gstProductCombo = QComboBox()
        self.gstProductCombo.addItem("Select saved product...")
        self.gstProductCombo.currentIndexChanged.connect(self.onProductSelected)
        productGroup['layout'].addWidget(self.gstProductCombo)
        pform = QFormLayout()
        pform.setSpacing(8)
        self.productNameInput = QLineEdit()
        self.productPriceInput = QLineEdit("0")
        self.productHsnInput = QLineEdit("19059010")
        self.productUnitInput = QLineEdit("Nos")
        pform.addRow("Product Name", self.productNameInput)
        pform.addRow("Default Price", self.productPriceInput)
        pform.addRow("HSN/SAC", self.productHsnInput)
        pform.addRow("Unit", self.productUnitInput)
        productGroup['layout'].addLayout(pform)
        saveProductBtn = QPushButton("Save Product")
        saveProductBtn.setObjectName("success")
        saveProductBtn.clicked.connect(self.saveCurrentProduct)
        applyProductBtn = QPushButton("Use Product In Next Row")
        applyProductBtn.setObjectName("secondary")
        applyProductBtn.clicked.connect(self.applySelectedProductToLastRow)
        productGroup['layout'].addWidget(saveProductBtn)
        productGroup['layout'].addWidget(applyProductBtn)
        layout.addWidget(productGroup['widget'])

        # Items Table
        itemsGroup = self.createSection("5) Items")
        self.gstItemsTable = QTableWidget()
        self.gstItemsTable.setColumnCount(13)
        self.gstItemsTable.setHorizontalHeaderLabels([
            'Description', 'HSN/Acc', 'Qty', 'MRP', 'Unit Price', 'Total',
            'Disc %', 'Taxable Val', 'CGST%', 'CGST Amt', 'SGST%', 'SGST Amt', 'Remove'
        ])
        self.setupGSTItemsTable(self.gstItemsTable)
        itemsGroup['layout'].addWidget(self.gstItemsTable)
        
        addItemBtn = QPushButton('+ Add Item')
        addItemBtn.setObjectName("success")
        addItemBtn.clicked.connect(lambda: self.addGSTItemToTable(self.gstItemsTable))
        itemsGroup['layout'].addWidget(addItemBtn)
        layout.addWidget(itemsGroup['widget'])

        # Summary
        summaryGroup = self.createSection(
            f"6) Summary (with {((self.GST_CGST_RATE + self.GST_SGST_RATE) * 100):.0f}% GST: "
            f"{self.GST_CGST_RATE * 100:.1f}% CGST + {self.GST_SGST_RATE * 100:.1f}% SGST)"
        )
        self.gstSubtotal = QLabel("Subtotal: ₹0.00")
        self.gstCGST = QLabel("CGST (2.5%): ₹0.00")
        self.gstSGST = QLabel("SGST (2.5%): ₹0.00")
        self.gstTotal = QLabel("Total: ₹0.00")
        self.gstNetPayable = QLabel("Net Payable: ₹0.00")
        summaryFont = QFont()
        summaryFont.setPointSize(11)
        self.gstTotal.setFont(summaryFont)
        self.gstNetPayable.setFont(summaryFont)
        self.gstTotal.setProperty("variant", "highlight")
        self.gstNetPayable.setProperty("variant", "success")
        summaryGroup['layout'].addWidget(self.gstSubtotal)
        summaryGroup['layout'].addWidget(self.gstCGST)
        summaryGroup['layout'].addWidget(self.gstSGST)
        summaryGroup['layout'].addWidget(self.gstTotal)
        summaryGroup['layout'].addWidget(self.gstNetPayable)
        layout.addWidget(summaryGroup['widget'])

        previewGroup = self.createSection("7) Live Preview")
        self.gstLivePreview = QTextEdit()
        self.gstLivePreview.setReadOnly(True)
        self.gstLivePreview.setMinimumHeight(180)
        previewGroup['layout'].addWidget(self.gstLivePreview)
        layout.addWidget(previewGroup['widget'])

        # Buttons
        btnLayout = QHBoxLayout()
        previewBtn = QPushButton('Preview & Print (3 Copies)')
        previewBtn.setObjectName("primary")
        previewBtn.clicked.connect(lambda: self.previewGSTInvoice(itemsGroup))
        exportBtn = QPushButton("Export CSV/Excel")
        exportBtn.setObjectName("secondary")
        exportBtn.clicked.connect(self.exportCurrentGSTData)
        btnLayout.addStretch()
        btnLayout.addWidget(exportBtn)
        btnLayout.addWidget(previewBtn)
        layout.addLayout(btnLayout)

        layout.addStretch()
        for field in self.gstFields.values():
            if isinstance(field, QLineEdit):
                field.textChanged.connect(self.refreshLivePreview)
            elif isinstance(field, QTextEdit):
                field.textChanged.connect(self.refreshLivePreview)
        self.loadCustomerProfiles()
        self.loadProductProfiles()
        self.generateInvoiceNumber()
        self.refreshLivePreview()
        return self.wrapInScrollArea(widget)

    def wrapInScrollArea(self, contentWidget):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(contentWidget)
        return scroll

    def createSection(self, title):
        widget = QGroupBox(title)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        return {'widget': widget, 'layout': layout}

    def addInputField(self, layout, label, placeholder):
        labelWidget = QLabel(label)
        layout.addWidget(labelWidget)
        lineEdit = QLineEdit()
        lineEdit.setPlaceholderText(placeholder)
        lineEdit.setMinimumHeight(34)
        layout.addWidget(lineEdit)
        return lineEdit

    def addTextArea(self, layout, label, rows):
        labelWidget = QLabel(label)
        layout.addWidget(labelWidget)
        textEdit = QTextEdit()
        textEdit.setMaximumHeight(rows * 25)
        layout.addWidget(textEdit)
        return textEdit

    def addDateField(self, layout, label):
        labelWidget = QLabel(label)
        layout.addWidget(labelWidget)
        # For simplicity, using QLineEdit with date
        lineEdit = QLineEdit()
        lineEdit.setText(datetime.now().strftime("%d-%m-%Y"))
        lineEdit.setPlaceholderText("DD-MM-YYYY")
        lineEdit.setInputMask("99-99-9999;_")
        lineEdit.setMinimumHeight(34)
        layout.addWidget(lineEdit)
        return lineEdit

    def addItemToTable(self, table):
        rowCount = table.rowCount()
        table.insertRow(rowCount)
        table.blockSignals(True)
        table.setItem(rowCount, 0, QTableWidgetItem(""))
        qtyItem = QTableWidgetItem("1")
        qtyItem.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        table.setItem(rowCount, 1, qtyItem)
        priceItem = QTableWidgetItem("0.00")
        priceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        table.setItem(rowCount, 2, priceItem)
        amountItem = QTableWidgetItem("₹0.00")
        amountItem.setFlags(amountItem.flags() & ~Qt.ItemIsEditable)
        amountItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        table.setItem(rowCount, 3, amountItem)
        table.blockSignals(False)

        removeBtn = QPushButton("Remove")
        removeBtn.setObjectName("danger")
        removeBtn.clicked.connect(lambda _=False, t=table, b=removeBtn: self.removeItemFromTable(t, b))
        table.setCellWidget(rowCount, 4, removeBtn)
        self.updateTableRowAmount(table, rowCount)
        self.updateSummaryFromTable(table)

    def setupItemsTable(self, table):
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Interactive)
        table.setColumnWidth(1, 90)
        table.setColumnWidth(2, 130)
        table.setColumnWidth(3, 120)
        table.setColumnWidth(4, 100)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setDefaultSectionSize(34)
        table.itemChanged.connect(lambda item, t=table: self.onTableItemChanged(t, item))
        table.setRowCount(0)
        self.addItemToTable(table)

    def removeItemFromTable(self, table, button):
        for row in range(table.rowCount()):
            # Find which column the remove button is in
            remove_col = table.columnCount() - 1
            if table.cellWidget(row, remove_col) is button:
                table.removeRow(row)
                break
        if table.rowCount() == 0:
            if table.columnCount() == 5:
                self.addItemToTable(table)
            else:
                self.addGSTItemToTable(table)
        self.updateSummaryFromTable(table)

    def setupGSTItemsTable(self, table):
        for c in range(table.columnCount()):
            if c == 12: # Remove button
                table.horizontalHeader().setSectionResizeMode(c, QHeaderView.Fixed)
                table.setColumnWidth(c, 70)
            elif c in [1, 6, 7]: # HSN, Disc, Taxable Val
                table.horizontalHeader().setSectionResizeMode(c, QHeaderView.Interactive)
                table.setColumnWidth(c, 80)
            elif c == 0:
                table.horizontalHeader().setSectionResizeMode(c, QHeaderView.Stretch)
            else:
                table.horizontalHeader().setSectionResizeMode(c, QHeaderView.Interactive)
                table.setColumnWidth(c, 80)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setDefaultSectionSize(34)
        table.itemChanged.connect(lambda item, t=table: self.onGSTTableItemChanged(t, item))
        table.setRowCount(0)
        self.addGSTItemToTable(table)

    def addGSTItemToTable(self, table):
        rowCount = table.rowCount()
        table.insertRow(rowCount)
        table.blockSignals(True)
        # 0: Description
        table.setItem(rowCount, 0, QTableWidgetItem(""))
        # 1: HSN/Acc
        hsnItem = QTableWidgetItem("")
        table.setItem(rowCount, 1, hsnItem)
        # 2: Qty
        qtyItem = QTableWidgetItem("1")
        qtyItem.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        table.setItem(rowCount, 2, qtyItem)
        # 3: MRP
        mrpItem = QTableWidgetItem("0.00")
        mrpItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        table.setItem(rowCount, 3, mrpItem)
        # 4: Unit Price
        priceItem = QTableWidgetItem("0.00")
        priceItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        table.setItem(rowCount, 4, priceItem)
        # 5: Total (read-only)
        totalItem = QTableWidgetItem("0.00")
        totalItem.setFlags(totalItem.flags() & ~Qt.ItemIsEditable)
        totalItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        table.setItem(rowCount, 5, totalItem)
        # 6: Disc %
        discItem = QTableWidgetItem("")
        table.setItem(rowCount, 6, discItem)
        # 7: Taxable Value
        taxableItem = QTableWidgetItem("")
        table.setItem(rowCount, 7, taxableItem)
        
        # 8: CGST%
        cgstPctItem = QTableWidgetItem(f"{self.GST_CGST_RATE * 100:.1f}")
        table.setItem(rowCount, 8, cgstPctItem)
        # 9: CGST Amt (read-only)
        cgstAmtItem = QTableWidgetItem("0.00")
        cgstAmtItem.setFlags(cgstAmtItem.flags() & ~Qt.ItemIsEditable)
        cgstAmtItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        table.setItem(rowCount, 9, cgstAmtItem)
        
        # 10: SGST%
        sgstPctItem = QTableWidgetItem(f"{self.GST_SGST_RATE * 100:.1f}")
        table.setItem(rowCount, 10, sgstPctItem)
        # 11: SGST Amt (read-only)
        sgstAmtItem = QTableWidgetItem("0.00")
        sgstAmtItem.setFlags(sgstAmtItem.flags() & ~Qt.ItemIsEditable)
        sgstAmtItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        table.setItem(rowCount, 11, sgstAmtItem)
        
        table.blockSignals(False)

        removeBtn = QPushButton("X")
        removeBtn.setObjectName("danger")
        removeBtn.clicked.connect(lambda _=False, t=table, b=removeBtn: self.removeItemFromTable(t, b))
        table.setCellWidget(rowCount, 12, removeBtn)
        self.updateGSTTableRowAmount(table, rowCount)
        self.updateSummaryFromTable(table)

    def onTableItemChanged(self, table, item):
        if not item:
            return
        row = item.row()
        col = item.column()
        if col == 1:
            qty = self.parse_positive_int(item.text(), default=1)
            table.blockSignals(True)
            item.setText(str(qty))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            table.blockSignals(False)
        elif col == 2:
            price = self.parse_non_negative_float(item.text(), default=0.0)
            table.blockSignals(True)
            item.setText(f"{price:.2f}")
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.blockSignals(False)

        if col in (0, 1, 2):
            self.updateTableRowAmount(table, row)
            self.updateSummaryFromTable(table)

    def parse_positive_int(self, value, default=1):
        try:
            parsed = int(str(value).strip())
            return parsed if parsed > 0 else default
        except (TypeError, ValueError):
            return default

    def parse_non_negative_float(self, value, default=0.0):
        try:
            parsed = float(str(value).strip())
            return parsed if parsed >= 0 else default
        except (TypeError, ValueError):
            return default

    def getRowTotals(self, table, row):
        qtyItem = table.item(row, 1)
        priceItem = table.item(row, 2)
        qty = self.parse_positive_int(qtyItem.text() if qtyItem else "", default=1)
        price = self.parse_non_negative_float(priceItem.text() if priceItem else "", default=0.0)
        return qty, price, qty * price

    def updateTableRowAmount(self, table, row):
        if row < 0 or row >= table.rowCount():
            return
        _, _, amount = self.getRowTotals(table, row)
        amountItem = table.item(row, 3)
        if amountItem is None:
            amountItem = QTableWidgetItem()
            amountItem.setFlags(amountItem.flags() & ~Qt.ItemIsEditable)
            amountItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 3, amountItem)
        table.blockSignals(True)
        amountItem.setText(f"₹{amount:.2f}")
        table.blockSignals(False)

    def onGSTTableItemChanged(self, table, item):
        if not item:
            return
        row = item.row()
        col = item.column()
        
        table.blockSignals(True)
        if col == 2: # Qty
            val = self.parse_positive_int(item.text(), default=1)
            item.setText(str(val))
            item.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        elif col in [3, 4, 8, 10]: # MRP, Unit Price, CGST%, SGST%
            val = self.parse_non_negative_float(item.text(), default=0.0)
            item.setText(f"{val:.2f}")
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        table.blockSignals(False)
        
        if col in [0, 2, 4, 8, 10]:
            self.updateGSTTableRowAmount(table, row)
            self.updateSummaryFromTable(table)

    def getGSTRowTotals(self, table, row):
        qty = self.parse_positive_int(table.item(row, 2).text() if table.item(row, 2) else "1", 1)
        price = self.parse_non_negative_float(table.item(row, 4).text() if table.item(row, 4) else "0.0", 0.0)
        mrp = self.parse_non_negative_float(table.item(row, 3).text() if table.item(row, 3) else "0.0", 0.0)
        cgst_pct = self.parse_non_negative_float(table.item(row, 8).text() if table.item(row, 8) else f"{self.GST_CGST_RATE*100}", self.GST_CGST_RATE*100)
        sgst_pct = self.parse_non_negative_float(table.item(row, 10).text() if table.item(row, 10) else f"{self.GST_SGST_RATE*100}", self.GST_SGST_RATE*100)
        
        total = qty * price
        cgst = total * (cgst_pct / 100.0)
        sgst = total * (sgst_pct / 100.0)
        return qty, price, mrp, total, cgst_pct, cgst, sgst_pct, sgst

    def updateGSTTableRowAmount(self, table, row):
        if row < 0 or row >= table.rowCount():
            return
        _, _, _, total, _, cgst, _, sgst = self.getGSTRowTotals(table, row)
        
        totalItem = table.item(row, 5)
        if not totalItem:
            totalItem = QTableWidgetItem()
            totalItem.setFlags(totalItem.flags() & ~Qt.ItemIsEditable)
            totalItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 5, totalItem)
            
        cgstItem = table.item(row, 9)
        if not cgstItem:
            cgstItem = QTableWidgetItem()
            cgstItem.setFlags(cgstItem.flags() & ~Qt.ItemIsEditable)
            cgstItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 9, cgstItem)
            
        sgstItem = table.item(row, 11)
        if not sgstItem:
            sgstItem = QTableWidgetItem()
            sgstItem.setFlags(sgstItem.flags() & ~Qt.ItemIsEditable)
            sgstItem.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            table.setItem(row, 11, sgstItem)
            
        table.blockSignals(True)
        totalItem.setText(f"{total:.2f}")
        cgstItem.setText(f"{cgst:.2f}")
        sgstItem.setText(f"{sgst:.2f}")
        table.blockSignals(False)

    def applyAppStyle(self):
        self.setStyleSheet("""
            QWidget {
                font-family: "Segoe UI";
                font-size: 13px;
                color: #1f2937;
            }
            QLabel[variant="highlight"] {
                color: #2563eb;
                font-weight: 700;
            }
            QLabel[variant="title"] {
                color: #111827;
                padding: 8px 4px;
            }
            QLabel[variant="success"] {
                color: #16a34a;
                font-weight: 700;
            }
            QLineEdit, QTextEdit, QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 6px 8px;
                background: #ffffff;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #2563eb;
            }
            QGroupBox {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
                color: #374151;
                font-weight: 600;
            }
            QTableWidget {
                gridline-color: #e5e7eb;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
            }
            QHeaderView::section {
                background: #f3f4f6;
                border: 1px solid #e5e7eb;
                padding: 6px;
                font-weight: 600;
            }
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                font-weight: 600;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton#secondary {
                background-color: #f3f4f6;
                color: #111827;
            }
            QPushButton#success {
                background-color: #16a34a;
                color: #ffffff;
            }
            QPushButton#danger {
                background-color: #ef4444;
                color: #ffffff;
            }
        """)

    def calculateSubtotalFromTable(self, table):
        subtotal = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        for row in range(table.rowCount()):
            descItem = table.item(row, 0)
            desc = descItem.text().strip() if descItem and descItem.text() else ""
            if not desc:
                continue
            if table is self.normalItemsTable:
                _, _, amount = self.getRowTotals(table, row)
                subtotal += amount
            else:
                _, _, _, amount, _, cgst, _, sgst = self.getGSTRowTotals(table, row)
                subtotal += amount
                total_cgst += cgst
                total_sgst += sgst
        return subtotal, total_cgst, total_sgst

    def updateSummaryFromTable(self, table):
        subtotal, total_cgst, total_sgst = self.calculateSubtotalFromTable(table)
        if table is self.normalItemsTable:
            if not hasattr(self, "normalSubtotal"):
                return
            tax = subtotal * self.NORMAL_TAX_RATE
            total = subtotal + tax
            self.normalSubtotal.setText(f"Subtotal: ₹{subtotal:.2f}")
            self.normalTax.setText(f"Tax ({int(self.NORMAL_TAX_RATE * 100)}%): ₹{tax:.2f}")
            self.normalTotal.setText(f"Total: ₹{total:.2f}")
        elif table is self.gstItemsTable:
            if not hasattr(self, "gstSubtotal"):
                return
            cgst = total_cgst
            sgst = total_sgst
            total = subtotal + cgst + sgst
            previous_balance = self.parse_non_negative_float(self.gstFields['previousBalance'].text(), 0.0) if hasattr(self, "gstFields") else 0.0
            advance = self.parse_non_negative_float(self.gstFields['advanceReceived'].text(), 0.0) if hasattr(self, "gstFields") else 0.0
            round_off = self.parse_non_negative_float(self.gstFields['roundOff'].text(), 0.0) if hasattr(self, "gstFields") else 0.0
            if hasattr(self, "gstFields") and self.gstFields['roundOff'].text().strip().startswith("-"):
                round_off = -round_off
            net_payable = total + previous_balance - advance + round_off
            self.gstSubtotal.setText(f"Subtotal: ₹{subtotal:.2f}")
            self.gstCGST.setText(f"CGST: ₹{cgst:.2f}")
            self.gstSGST.setText(f"SGST: ₹{sgst:.2f}")
            self.gstTotal.setText(f"Total: ₹{total:.2f}")
            self.gstNetPayable.setText(f"Net Payable: ₹{net_payable:.2f}")
            self.refreshLivePreview()

    def previewNormalInvoice(self, invoiceGroup, companyGroup, itemsGroup):
        data = {
            'invoiceNumber': invoiceGroup['invoiceNumber'].text(),
            'date': invoiceGroup['date'].text(),
            'vendorName': companyGroup['vendorName'].text(),
            'vendorAddress': companyGroup['vendorAddress'].toPlainText(),
            'items': self.getItemsFromTable(self.normalItemsTable)
        }
        
        if not data['invoiceNumber'] or not data['vendorName']:
            QMessageBox.warning(self, 'Incomplete Form', 'Please fill Invoice Number and Vendor Name')
            return
        if not data['items']:
            QMessageBox.warning(self, 'No Items', 'Please add at least one valid item with description.')
            return

        self.generateAndPrintNormalPDF(data)

    def previewGSTInvoice(self, itemsGroup):
        data = self.buildGSTInvoiceData()
        if not data['invoiceNumber'] or not data['vendorName']:
            QMessageBox.warning(self, 'Incomplete Form', 'Please fill Invoice Number and Vendor Name')
            return
        if not data['items']:
            QMessageBox.warning(self, 'No Items', 'Please add at least one valid item with description.')
            return

        self.generateAndPrintGSTPDF(data)

    def buildGSTInvoiceData(self):
        selected_copies = []
        if self.copyVendorCheck.isChecked():
            selected_copies.append(self.GST_COPY_LABELS[0])
        if self.copyDistributorCheck.isChecked():
            selected_copies.append(self.GST_COPY_LABELS[1])
        if self.copyOfficialCheck.isChecked():
            selected_copies.append(self.GST_COPY_LABELS[2])
        if not selected_copies:
            selected_copies = [self.GST_COPY_LABELS[0]]

        subtotal, total_cgst, total_sgst = self.calculateSubtotalFromTable(self.gstItemsTable)
        cgst = total_cgst
        sgst = total_sgst
        total_tax = cgst + sgst
        gross_total = subtotal + total_tax
        previous_balance = self.parse_non_negative_float(self.gstFields['previousBalance'].text(), 0.0)
        advance_received = self.parse_non_negative_float(self.gstFields['advanceReceived'].text(), 0.0)
        round_off_text = self.gstFields['roundOff'].text().strip()
        round_off = self.parse_non_negative_float(round_off_text, 0.0)
        if round_off_text.startswith("-"):
            round_off = -round_off
        net_payable = gross_total + previous_balance - advance_received + round_off

        data = {
            'invoiceNumber': self.gstFields['invoiceNumber'].text().strip(),
            'date': self.gstFields['date'].text().strip(),
            'vendorName': self.gstFields['vendorName'].text().strip(),
            'vendorAddress': self.gstFields['vendorAddress'].toPlainText().strip(),
            'vendorGST': self.gstFields['vendorGST'].text().strip(),
            'vendorContact': self.gstFields['vendorContact'].text().strip(),
            'vendorState': self.gstFields['vendorState'].text().strip(),
            'vendorPin': self.gstFields['vendorPin'].text().strip(),
            'placeOfSupply': self.gstFields['placeOfSupply'].text().strip(),
            'vehicleNumber': self.gstFields['vehicleNumber'].text().strip(),
            'hsnSac': self.gstFields['hsnSac'].text().strip(),
            'unitName': self.gstFields['unitName'].text().strip(),
            'previousBalance': previous_balance,
            'advanceReceived': advance_received,
            'roundOff': round_off,
            'subtotal': subtotal,
            'cgstAmount': cgst,
            'sgstAmount': sgst,
            'totalTax': total_tax,
            'grossTotal': gross_total,
            'netPayable': net_payable,
            'items': self.getItemsFromTable(self.gstItemsTable),
            'copies': len(selected_copies),
            'copyLabels': selected_copies,
            'createdAt': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        return data

    def getItemsFromTable(self, table):
        items = []
        for row in range(table.rowCount()):
            desc = table.item(row, 0)
            description = desc.text().strip() if desc and desc.text() else ""
            if description:
                if table is self.normalItemsTable:
                    quantity, price, _ = self.getRowTotals(table, row)
                    items.append({
                        'description': description,
                        'quantity': quantity,
                        'price': price
                    })
                else:
                    qty, price, mrp, total, cgst_pct, cgst, sgst_pct, sgst = self.getGSTRowTotals(table, row)
                    hsn = table.item(row, 1).text() if table.item(row, 1) else ""
                    disc = table.item(row, 6).text() if table.item(row, 6) else ""
                    taxable = table.item(row, 7).text() if table.item(row, 7) else ""
                    items.append({
                        'description': description,
                        'hsn': hsn,
                        'quantity': qty,
                        'mrp': mrp,
                        'price': price,
                        'total': total,
                        'disc': disc,
                        'taxable': taxable,
                        'cgst_pct': cgst_pct,
                        'cgst': cgst,
                        'sgst_pct': sgst_pct,
                        'sgst': sgst
                    })
        return items

    def generateAndPrintNormalPDF(self, data):
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save Invoice", f"Invoice_{data['invoiceNumber']}.pdf", "PDF Files (*.pdf)"
        )
        if fileName:
            self.createNormalPDF(fileName, data)
            QMessageBox.information(self, 'Success', f'Invoice saved to {fileName}')

    def generateAndPrintGSTPDF(self, data):
        fileName, _ = QFileDialog.getSaveFileName(
            self, "Save Invoice", f"Invoice_{data['invoiceNumber']}.pdf", "PDF Files (*.pdf)"
        )
        if fileName:
            self.createGSTPDF(fileName, data)
            self.saveInvoiceAudit(data, fileName)
            self.loadInvoiceHistory()
            self.createAndEmailGstCopies(fileName, data)
            QMessageBox.information(self, 'Success', f'GST Invoice ({data["copies"]} copies) saved to {fileName}')

    def createAndEmailGstCopies(self, base_pdf_path, data):
        copy_labels = data.get('copyLabels') or self.GST_COPY_LABELS
        if len(copy_labels) < 3:
            return
        base_path = Path(base_pdf_path)
        stem = base_path.stem
        distributor_pdf = base_path.with_name(f"{stem}_copy2_distributor.pdf")
        audit_pdf = base_path.with_name(f"{stem}_copy3_audit.pdf")

        distributor_data = dict(data)
        distributor_data['copyLabels'] = [copy_labels[1]]
        audit_data = dict(data)
        audit_data['copyLabels'] = [copy_labels[2]]

        self.createGSTPDF(str(distributor_pdf), distributor_data)
        self.createGSTPDF(str(audit_pdf), audit_data)

        invoice_no = data.get("invoiceNumber", "Invoice")
        invoice_date = data.get("date", "")
        subject_2 = f"GST Invoice Copy 2 (Distributor) - {invoice_no}"
        subject_3 = f"GST Invoice Copy 3 (Audit) - {invoice_no}"
        body_2 = f"Please find attached GST invoice Copy 2 (Distributor).\nInvoice No: {invoice_no}\nDate: {invoice_date}"
        body_3 = f"Please find attached GST invoice Copy 3 (Audit).\nInvoice No: {invoice_no}\nDate: {invoice_date}"

        self.openGmailCompose(self.DISTRIBUTOR_EMAIL, subject_2, body_2)
        self.openGmailCompose(self.AUDIT_EMAIL, subject_3, body_3)

        try:
            os.startfile(str(base_path.parent))
        except Exception:
            pass

    def openGmailCompose(self, to_addr, subject, body):
        if not to_addr:
            return
        qs = {
            "view": "cm",
            "to": to_addr,
            "su": subject,
            "body": body,
        }
        url = "https://mail.google.com/mail/?" + urllib.parse.urlencode(qs, quote_via=urllib.parse.quote)
        webbrowser.open(url, new=2)

    def createNormalPDF(self, fileName, data):
        doc = SimpleDocTemplate(fileName, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        
        # Company Header - Centered
        company_header = [
            ['RINA RICH FOOD & AGENCIES'],
            ['Aranauttukara, Thrissur, Kerala - 680301'],
            ['Phone: +91-9895314201']
        ]
        
        header_table = Table(company_header, colWidths=[6*inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 16),
            ('FONTSIZE', (0, 1), (0, 2), 10),
            ('BOTTOMPADDING', (0, 0), (0, 0), 8),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Invoice Title and Details
        invoice_header = [
            ['INVOICE', f"Invoice No: {data['invoiceNumber']}"],
            ['', f"Date: {data['date']}"],
        ]
        
        invoice_table = Table(invoice_header, colWidths=[3*inch, 3*inch])
        invoice_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 14),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        story.append(invoice_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Bill To Section
        bill_to_data = [
            ['Bill To:'],
            [data['vendorName']],
            [data['vendorAddress']]
        ]
        
        bill_table = Table(bill_to_data, colWidths=[6*inch])
        bill_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (0, 0), 12),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(bill_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Items Table
        items_data = [['S.No', 'Description of Goods', 'Qty', 'Rate', 'Amount']]
        subtotal = 0
        
        for idx, item in enumerate(data['items'], 1):
            amount = item['quantity'] * item['price']
            subtotal += amount
            items_data.append([
                str(idx),
                item['description'],
                str(item['quantity']),
                self.format_pdf_currency(item['price']),
                self.format_pdf_currency(amount)
            ])
        
        items_table = Table(items_data, colWidths=[0.6*inch, 3.2*inch, 0.8*inch, 1*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 0.1*inch))
        
        # Total Section
        tax = subtotal * self.NORMAL_TAX_RATE
        grand_total = subtotal + tax
        total_data = [
            ['', '', '', 'Subtotal:', self.format_pdf_currency(subtotal)],
            ['', '', '', f"Tax ({int(self.NORMAL_TAX_RATE * 100)}%):", self.format_pdf_currency(tax)],
            ['', '', '', 'Grand Total:', self.format_pdf_currency(grand_total)]
        ]
        
        total_table = Table(total_data, colWidths=[0.6*inch, 3.2*inch, 0.8*inch, 1*inch, 1.2*inch])
        total_table.setStyle(TableStyle([
            ('FONTNAME', (3, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (3, 0), (-1, -1), 11),
            ('ALIGN', (3, 0), (-1, -1), 'CENTER'),
            ('BOX', (3, 0), (-1, -1), 1, colors.black),
            ('INNERGRID', (3, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (3, 2), (-1, 2), colors.lightgrey),
        ]))
        story.append(total_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Terms and Conditions
        terms = Paragraph("<b>Terms & Conditions:</b><br/>1. Payment due within 30 days<br/>2. Thank you for your business!", styles['Normal'])
        story.append(terms)
        
        doc.build(story)

    def createGSTPDF(self, fileName, data):
        doc = SimpleDocTemplate(fileName, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()
        company_name = self.COMPANY_NAME
        company_address = self.COMPANY_ADDRESS
        company_phone = self.COMPANY_PHONE
        company_gstin = self.COMPANY_GSTIN
        company_state = self.COMPANY_STATE
        copy_labels = data.get('copyLabels') or self.GST_COPY_LABELS

        hsn = data.get('hsnSac', '').strip() or "19059010"
        unit = data.get('unitName', '').strip() or "Nos"
        place_of_supply = data.get('placeOfSupply', '').strip() or company_state
        vehicle_number = data.get('vehicleNumber', '').strip() or "-"
        vendor_state = data.get('vendorState', '').strip() or place_of_supply
        vendor_contact = data.get('vendorContact', '').strip() or "-"
        vendor_pin = data.get('vendorPin', '').strip() or "-"
        vendor_gstin = data.get('vendorGST', '').strip() or "-"

        subtotal = 0.0
        total_cgst = 0.0
        total_sgst = 0.0
        total_qty = 0
        item_rows = []
        for idx, item in enumerate(data['items'], 1):
            qty = item.get('quantity', 1)
            price = item.get('price', 0.0)
            mrp = item.get('mrp', 0.0)
            total = item.get('total', qty * price)
            cgst_pct = item.get('cgst_pct', self.GST_CGST_RATE * 100)
            cgst = item.get('cgst', total * (cgst_pct / 100))
            sgst_pct = item.get('sgst_pct', self.GST_SGST_RATE * 100)
            sgst = item.get('sgst', total * (sgst_pct / 100))
            item_hsn = item.get('hsn', hsn)
            disc = item.get('disc', '')
            taxable = item.get('taxable', '')

            subtotal += total
            total_cgst += cgst
            total_sgst += sgst
            total_qty += qty

            item_rows.append([
                str(idx),
                item['description'],
                item_hsn,
                str(qty),
                self.format_pdf_currency(mrp) if mrp else "",
                self.format_pdf_currency(price),
                self.format_pdf_currency(total),
                str(disc),
                str(taxable),
                f"{cgst_pct}%",
                self.format_pdf_currency(cgst),
                f"{sgst_pct}%",
                self.format_pdf_currency(sgst),
            ])

        total_tax = data.get('totalTax', total_cgst + total_sgst)
        grand_total = data.get('grossTotal', subtotal + total_tax)
        net_payable = data.get('netPayable', grand_total)
        previous_balance = data.get('previousBalance', 0.0)
        advance_received = data.get('advanceReceived', 0.0)
        round_off = data.get('roundOff', 0.0)
        amount_in_words = self.number_to_words(int(round(net_payable)))

        for copy in range(1, len(copy_labels) + 1):
            copy_index = min(copy - 1, len(copy_labels) - 1)
            invoice_title = Table(
                [[
                    '',
                    Paragraph("<b>TAX INVOICE</b>", styles['Normal']),
                    copy_labels[copy_index],
                ]],
                colWidths=[2.2 * inch, 2.2 * inch, 2.2 * inch]
            )
            invoice_title.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
                ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
                ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (1, 0), (1, 0), 14),
                ('FONTSIZE', (2, 0), (2, 0), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(invoice_title)

            company_block = Table([[
                Paragraph(
                    f"<b>{company_name}</b><br/>{company_address}<br/>Phone: {company_phone}<br/>"
                    f"State: {company_state} &nbsp;&nbsp;&nbsp;&nbsp; GSTIN: {company_gstin}",
                    styles['Normal']
                )
            ]], colWidths=[6.6 * inch])
            company_block.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(company_block)

            customer_and_invoice = Table([[
                Paragraph(
                    f"<b>Bill To:</b><br/>{data['vendorName']}<br/>{data['vendorAddress'].replace(chr(10), '<br/>')}<br/>"
                    f"Contact No: {vendor_contact} &nbsp;&nbsp; State: {vendor_state}<br/>PIN: {vendor_pin}<br/>GSTIN: {vendor_gstin}",
                    styles['Normal']
                ),
                Paragraph(
                    f"<b>Invoice Details:</b><br/>No: {data['invoiceNumber']}<br/>Date: {data['date']}<br/>"
                    f"Place Of Supply: {place_of_supply}<br/><br/><b>Transportation Details:</b><br/>"
                    f"Vehicle Number: {vehicle_number}",
                    styles['Normal']
                )
            ]], colWidths=[3.8 * inch, 2.8 * inch])
            customer_and_invoice.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(customer_and_invoice)

            items_data = [[
                '#', 'Desc', 'HSN', 'Qty', 'MRP',
                'Price', 'Total', 'Disc%', 'TaxVal', 'CGST%', 'CGST', 'SGST%', 'SGST'
            ]]
            items_data.extend(item_rows)
            items_data.append([
                '', 'Total', '', str(total_qty), '', '', self.format_pdf_currency(subtotal), '', '', '', self.format_pdf_currency(total_cgst), '', self.format_pdf_currency(total_sgst)
            ])

            items_table = Table(items_data, colWidths=[
                0.2 * inch, 1.5 * inch, 0.55 * inch, 0.3 * inch, 0.4 * inch, 0.5 * inch, 0.55 * inch, 0.3 * inch, 0.4 * inch, 0.35 * inch, 0.6 * inch, 0.35 * inch, 0.6 * inch
            ])
            items_table.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (1, 1), (1, -2), 'LEFT'),
                ('ALIGN', (4, 1), (6, -2), 'RIGHT'),
                ('ALIGN', (10, 1), (10, -2), 'RIGHT'),
                ('ALIGN', (12, 1), (12, -2), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), 6.5), # Smaller font to fit 13 columns
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(items_table)

            tax_summary = Table([
                ['HSN/SAC', f"Taxable Amount({self.PDF_CURRENCY})", 'CGST Rate',
                 f"CGST Amt({self.PDF_CURRENCY})", 'SGST Rate', f"SGST Amt({self.PDF_CURRENCY})",
                 f"Total Tax({self.PDF_CURRENCY})"],
                [hsn, f"{subtotal:.2f}", f"{self.GST_CGST_RATE * 100:.1f}%", f"{total_cgst:.2f}",
                 f"{self.GST_SGST_RATE * 100:.1f}%", f"{total_sgst:.2f}", f"{total_tax:.2f}"],
                ['TOTAL', f"{subtotal:.2f}", '', f"{total_cgst:.2f}", '', f"{total_sgst:.2f}", f"{total_tax:.2f}"],
            ], colWidths=[0.9 * inch, 1.1 * inch, 0.8 * inch, 0.9 * inch, 0.8 * inch, 0.9 * inch, 1.2 * inch])
            tax_summary.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 7.5),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ]))

            amount_panel = Table([
                ['Sub Total', self.format_pdf_currency(subtotal, space=True)],
                ['Total Tax', self.format_pdf_currency(total_tax, space=True)],
                ['Gross Total', self.format_pdf_currency(grand_total, space=True)],
                ['Previous Balance', self.format_pdf_currency(previous_balance, space=True)],
                ['Advance Received', self.format_pdf_currency(advance_received, space=True)],
                ['Round Off', self.format_pdf_currency(round_off, space=True)],
                ['Net Payable', self.format_pdf_currency(net_payable, space=True)],
                ['Invoice Amount in Words:', f"Rupees {amount_in_words} only"],
                ['Balance', self.format_pdf_currency(net_payable, space=True)],
            ], colWidths=[2.2 * inch, 4.4 * inch])
            amount_panel.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ALIGN', (1, 0), (1, 6), 'RIGHT'),
                ('ALIGN', (1, 7), (1, 7), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(tax_summary)
            story.append(amount_panel)

            terms = Table([[
                Paragraph(
                    "<b>Terms & Conditions:</b><br/>"
                    "Thanks for doing business with us!<br/>"
                    "Please note that goods sold are non-returnable.",
                    styles['Normal']
                )
            ]], colWidths=[6.6 * inch])
            terms.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(terms)

            bank_and_sign = Table([[
                Paragraph(
                    "<b>Bank Details:</b><br/>"
                    "Name: UNION BANK OF INDIA,THRISSUR<br/>"
                    "Account No: 117511010000036<br/>"
                    "IFSC code: UBIN0811751<br/>"
                    "Account holder's name:JOY RAPPAI",
                    styles['Normal']
                ),
                Paragraph(
                    f"<b>For {company_name}:</b><br/><br/><br/>Authorized Signatory",
                    styles['Normal']
                )
            ]], colWidths=[4.2 * inch, 2.4 * inch])
            bank_and_sign.setStyle(TableStyle([
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ]))
            story.append(bank_and_sign)

            if copy < len(copy_labels):
                story.append(PageBreak())

        doc.build(story)
    def format_pdf_currency(self, amount, space=False):
        prefix = f"{self.PDF_CURRENCY} " if space else self.PDF_CURRENCY
        return f"{prefix}{amount:.2f}"

    def createHistoryTab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        filterGroup = self.createSection("Invoice Search")
        filterForm = QFormLayout()
        self.historyCustomerFilter = QLineEdit()
        self.historyInvoiceFilter = QLineEdit()
        self.historyDateFilter = QLineEdit()
        filterForm.addRow("Customer", self.historyCustomerFilter)
        filterForm.addRow("Invoice Number", self.historyInvoiceFilter)
        filterForm.addRow("Date (DD-MM-YYYY)", self.historyDateFilter)
        filterGroup['layout'].addLayout(filterForm)

        filterBtnRow = QHBoxLayout()
        applyFilterBtn = QPushButton("Apply Filter")
        clearFilterBtn = QPushButton("Clear")
        applyFilterBtn.setObjectName("primary")
        clearFilterBtn.setObjectName("secondary")
        applyFilterBtn.clicked.connect(self.loadInvoiceHistory)
        clearFilterBtn.clicked.connect(self.clearHistoryFilters)
        filterBtnRow.addWidget(applyFilterBtn)
        filterBtnRow.addWidget(clearFilterBtn)
        filterGroup['layout'].addLayout(filterBtnRow)
        layout.addWidget(filterGroup['widget'])

        self.historyTable = QTableWidget()
        self.historyTable.setColumnCount(6)
        self.historyTable.setHorizontalHeaderLabels(
            ["Invoice No", "Date", "Customer", "GSTIN", "Net Payable", "PDF Path"]
        )
        self.historyTable.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.historyTable.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.historyTable.setSelectionBehavior(QTableWidget.SelectRows)
        self.historyTable.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.historyTable)

        historyBtnRow = QHBoxLayout()
        reprintBtn = QPushButton("Reprint Selected")
        exportSelectedBtn = QPushButton("Export Selected CSV")
        reprintBtn.setObjectName("primary")
        exportSelectedBtn.setObjectName("secondary")
        reprintBtn.clicked.connect(self.reprintSelectedInvoice)
        exportSelectedBtn.clicked.connect(self.exportSelectedHistoryInvoice)
        historyBtnRow.addStretch()
        historyBtnRow.addWidget(exportSelectedBtn)
        historyBtnRow.addWidget(reprintBtn)
        layout.addLayout(historyBtnRow)

        self.loadInvoiceHistory()
        return widget

    def clearHistoryFilters(self):
        self.historyCustomerFilter.clear()
        self.historyInvoiceFilter.clear()
        self.historyDateFilter.clear()
        self.loadInvoiceHistory()

    def loadCustomerProfiles(self):
        if not hasattr(self, "gstCustomerCombo"):
            return
        self.gstCustomerCombo.blockSignals(True)
        self.gstCustomerCombo.clear()
        self.gstCustomerCombo.addItem("Select saved customer...")
        for customer in self.customers:
            self.gstCustomerCombo.addItem(customer.get("vendorName", "Unnamed"), customer)
        self.gstCustomerCombo.blockSignals(False)

    def onCustomerSelected(self, index):
        if index <= 0:
            return
        customer = self.gstCustomerCombo.itemData(index)
        if not isinstance(customer, dict):
            return
        self.gstFields['vendorName'].setText(customer.get('vendorName', ''))
        self.gstFields['vendorAddress'].setPlainText(customer.get('vendorAddress', ''))
        self.gstFields['vendorGST'].setText(customer.get('vendorGST', ''))
        self.gstFields['vendorContact'].setText(customer.get('vendorContact', ''))
        self.gstFields['vendorState'].setText(customer.get('vendorState', ''))
        self.gstFields['vendorPin'].setText(customer.get('vendorPin', ''))
        self.refreshLivePreview()

    def saveCurrentCustomer(self):
        customer = {
            "vendorName": self.gstFields['vendorName'].text().strip(),
            "vendorAddress": self.gstFields['vendorAddress'].toPlainText().strip(),
            "vendorGST": self.gstFields['vendorGST'].text().strip(),
            "vendorContact": self.gstFields['vendorContact'].text().strip(),
            "vendorState": self.gstFields['vendorState'].text().strip(),
            "vendorPin": self.gstFields['vendorPin'].text().strip(),
        }
        if not customer["vendorName"]:
            QMessageBox.warning(self, "Missing Name", "Vendor name is required to save customer profile.")
            return
        self.customers = [c for c in self.customers if c.get("vendorName", "").lower() != customer["vendorName"].lower()]
        self.customers.append(customer)
        self.customers.sort(key=lambda c: c.get("vendorName", "").lower())
        self.saveJson(self.customersFile, self.customers)
        self.loadCustomerProfiles()
        QMessageBox.information(self, "Saved", "Customer profile saved.")

    def loadProductProfiles(self):
        if not hasattr(self, "gstProductCombo"):
            return
        self.gstProductCombo.blockSignals(True)
        self.gstProductCombo.clear()
        self.gstProductCombo.addItem("Select saved product...")
        for product in self.products:
            self.gstProductCombo.addItem(product.get("name", "Unnamed"), product)
        self.gstProductCombo.blockSignals(False)

    def onProductSelected(self, index):
        if index <= 0:
            return
        product = self.gstProductCombo.itemData(index)
        if not isinstance(product, dict):
            return
        self.productNameInput.setText(product.get("name", ""))
        self.productPriceInput.setText(str(product.get("price", 0)))
        self.productHsnInput.setText(product.get("hsnSac", "19059010"))
        self.productUnitInput.setText(product.get("unitName", "Nos"))

    def saveCurrentProduct(self):
        name = self.productNameInput.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Product name is required.")
            return
        price = self.parse_non_negative_float(self.productPriceInput.text(), 0.0)
        product = {
            "name": name,
            "price": price,
            "hsnSac": self.productHsnInput.text().strip() or "19059010",
            "unitName": self.productUnitInput.text().strip() or "Nos",
        }
        self.products = [p for p in self.products if p.get("name", "").lower() != name.lower()]
        self.products.append(product)
        self.products.sort(key=lambda p: p.get("name", "").lower())
        self.saveJson(self.productsFile, self.products)
        self.loadProductProfiles()
        QMessageBox.information(self, "Saved", "Product profile saved.")

    def applySelectedProductToLastRow(self):
        name = self.productNameInput.text().strip()
        if not name:
            QMessageBox.warning(self, "No Product", "Select or enter a product first.")
            return
        price = self.parse_non_negative_float(self.productPriceInput.text(), 0.0)
        
        row = self.gstItemsTable.rowCount() - 1
        if row < 0:
            self.addGSTItemToTable(self.gstItemsTable)
            row = self.gstItemsTable.rowCount() - 1
            
        self.gstItemsTable.blockSignals(True)
        # 0: Description
        self.gstItemsTable.item(row, 0).setText(name)
        # 1: HSN
        self.gstItemsTable.item(row, 1).setText(self.productHsnInput.text().strip() or "19059010")
        # 4: Unit Price
        self.gstItemsTable.item(row, 4).setText(f"{price:.2f}")
        self.gstItemsTable.blockSignals(False)
        self.updateGSTTableRowAmount(self.gstItemsTable, row)
        self.updateSummaryFromTable(self.gstItemsTable)

    def generateInvoiceNumber(self):
        now = datetime.now()
        fy_start = now.year if now.month >= 4 else now.year - 1
        fy_end_short = str((fy_start + 1) % 100).zfill(2)
        fy_key = f"{fy_start}-{fy_end_short}"
        next_num = int(self.counters.get(fy_key, 0)) + 1
        self.counters[fy_key] = next_num
        self.saveJson(self.countersFile, self.counters)
        self.gstFields['invoiceNumber'].setText(f"{str(fy_start)[-2:]}-{fy_end_short}/INV/{next_num:04d}")

    def refreshLivePreview(self):
        if not hasattr(self, "gstLivePreview"):
            return
        data = self.buildGSTInvoiceData() if hasattr(self, "gstFields") else {}
        lines = [
            f"Invoice: {data.get('invoiceNumber', '-')}",
            f"Date: {data.get('date', '-')}",
            f"Customer: {data.get('vendorName', '-')}",
            f"GSTIN: {data.get('vendorGST', '-')}",
            f"Place Of Supply: {data.get('placeOfSupply', '-')}",
            f"Items: {len(data.get('items', []))}",
            f"Subtotal: ₹{data.get('subtotal', 0):.2f}",
            f"CGST: ₹{data.get('cgstAmount', 0):.2f}",
            f"SGST: ₹{data.get('sgstAmount', 0):.2f}",
            f"Gross Total: ₹{data.get('grossTotal', 0):.2f}",
            f"Previous Balance: ₹{data.get('previousBalance', 0):.2f}",
            f"Advance Received: ₹{data.get('advanceReceived', 0):.2f}",
            f"Round Off: ₹{data.get('roundOff', 0):.2f}",
            f"Net Payable: ₹{data.get('netPayable', 0):.2f}",
            "Copies: " + ", ".join(data.get('copyLabels', [])),
        ]
        self.gstLivePreview.setPlainText("\n".join(lines))

    def exportCurrentGSTData(self):
        data = self.buildGSTInvoiceData()
        if not data.get("items"):
            QMessageBox.warning(self, "No Data", "Add at least one item before exporting.")
            return
        default_name = f"Invoice_{data['invoiceNumber'].replace('/', '_')}"
        csv_path, _ = QFileDialog.getSaveFileName(self, "Export CSV", default_name + ".csv", "CSV Files (*.csv)")
        if not csv_path:
            return
        self.exportInvoiceCSV(csv_path, data)
        excel_msg = self.exportInvoiceExcel(csv_path.replace(".csv", ".xlsx"), data)
        QMessageBox.information(self, "Export Complete", f"CSV exported to:\n{csv_path}\n{excel_msg}")

    def exportInvoiceCSV(self, csv_path, data):
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Invoice Number", data.get("invoiceNumber", "")])
            writer.writerow(["Date", data.get("date", "")])
            writer.writerow(["Customer", data.get("vendorName", "")])
            writer.writerow(["Customer GSTIN", data.get("vendorGST", "")])
            writer.writerow([])
            writer.writerow(["Description", "Qty", "Unit Price", "Amount"])
            for item in data.get("items", []):
                writer.writerow([
                    item.get("description", ""),
                    item.get("quantity", 0),
                    f"{item.get('price', 0):.2f}",
                    f"{item.get('quantity', 0) * item.get('price', 0):.2f}",
                ])
            writer.writerow([])
            writer.writerow(["Subtotal", f"{data.get('subtotal', 0):.2f}"])
            writer.writerow(["CGST", f"{data.get('cgstAmount', 0):.2f}"])
            writer.writerow(["SGST", f"{data.get('sgstAmount', 0):.2f}"])
            writer.writerow(["Gross Total", f"{data.get('grossTotal', 0):.2f}"])
            writer.writerow(["Net Payable", f"{data.get('netPayable', 0):.2f}"])

    def exportInvoiceExcel(self, xlsx_path, data):
        try:
            from openpyxl import Workbook
        except Exception:
            return "Excel skipped (install openpyxl for .xlsx export)."
        wb = Workbook()
        ws = wb.active
        ws.title = "Invoice"
        ws.append(["Invoice Number", data.get("invoiceNumber", "")])
        ws.append(["Date", data.get("date", "")])
        ws.append(["Customer", data.get("vendorName", "")])
        ws.append(["Customer GSTIN", data.get("vendorGST", "")])
        ws.append([])
        ws.append(["Description", "Qty", "Unit Price", "Amount"])
        for item in data.get("items", []):
            ws.append([
                item.get("description", ""),
                item.get("quantity", 0),
                item.get("price", 0),
                item.get("quantity", 0) * item.get("price", 0),
            ])
        ws.append([])
        ws.append(["Subtotal", data.get("subtotal", 0)])
        ws.append(["CGST", data.get("cgstAmount", 0)])
        ws.append(["SGST", data.get("sgstAmount", 0)])
        ws.append(["Gross Total", data.get("grossTotal", 0)])
        ws.append(["Net Payable", data.get("netPayable", 0)])
        wb.save(xlsx_path)
        return f"Excel exported to:\n{xlsx_path}"

    def saveInvoiceAudit(self, data, pdf_path):
        safe_invoice = data.get("invoiceNumber", "invoice").replace("/", "_").replace("\\", "_")
        json_path = self.invoicesDir / f"{safe_invoice}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        payload = dict(data)
        payload["pdfPath"] = str(pdf_path)
        payload["savedAt"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.saveJson(json_path, payload)
        self.invoiceIndex.append({
            "invoiceNumber": payload.get("invoiceNumber", ""),
            "date": payload.get("date", ""),
            "vendorName": payload.get("vendorName", ""),
            "vendorGST": payload.get("vendorGST", ""),
            "netPayable": payload.get("netPayable", 0.0),
            "pdfPath": str(pdf_path),
            "jsonPath": str(json_path),
            "savedAt": payload["savedAt"],
        })
        self.saveJson(self.indexFile, self.invoiceIndex)

    def loadInvoiceHistory(self):
        if not hasattr(self, "historyTable"):
            return
        customer_q = self.historyCustomerFilter.text().strip().lower() if hasattr(self, "historyCustomerFilter") else ""
        invoice_q = self.historyInvoiceFilter.text().strip().lower() if hasattr(self, "historyInvoiceFilter") else ""
        date_q = self.historyDateFilter.text().strip() if hasattr(self, "historyDateFilter") else ""
        filtered = []
        for row in self.invoiceIndex:
            if customer_q and customer_q not in row.get("vendorName", "").lower():
                continue
            if invoice_q and invoice_q not in row.get("invoiceNumber", "").lower():
                continue
            if date_q and date_q != row.get("date", ""):
                continue
            filtered.append(row)
        self.historyTable.setRowCount(len(filtered))
        for r, row in enumerate(filtered):
            self.historyTable.setItem(r, 0, QTableWidgetItem(row.get("invoiceNumber", "")))
            self.historyTable.setItem(r, 1, QTableWidgetItem(row.get("date", "")))
            self.historyTable.setItem(r, 2, QTableWidgetItem(row.get("vendorName", "")))
            self.historyTable.setItem(r, 3, QTableWidgetItem(row.get("vendorGST", "")))
            self.historyTable.setItem(r, 4, QTableWidgetItem(f"₹{float(row.get('netPayable', 0)):.2f}"))
            self.historyTable.setItem(r, 5, QTableWidgetItem(row.get("pdfPath", "")))
            for c in range(6):
                item = self.historyTable.item(r, c)
                item.setData(Qt.UserRole, row.get("jsonPath", ""))

    def getSelectedHistoryPayload(self):
        row = self.historyTable.currentRow()
        if row < 0:
            return None
        item = self.historyTable.item(row, 0)
        if not item:
            return None
        json_path = item.data(Qt.UserRole)
        if not json_path:
            return None
        payload = self.loadJson(Path(json_path), None)
        return payload

    def reprintSelectedInvoice(self):
        payload = self.getSelectedHistoryPayload()
        if not payload:
            QMessageBox.warning(self, "No Selection", "Select one invoice row first.")
            return
        out, _ = QFileDialog.getSaveFileName(
            self,
            "Save Reprint PDF",
            f"Reprint_{payload.get('invoiceNumber', 'Invoice')}.pdf",
            "PDF Files (*.pdf)"
        )
        if not out:
            return
        self.createGSTPDF(out, payload)
        QMessageBox.information(self, "Done", f"Reprinted invoice saved to {out}")

    def exportSelectedHistoryInvoice(self):
        payload = self.getSelectedHistoryPayload()
        if not payload:
            QMessageBox.warning(self, "No Selection", "Select one invoice row first.")
            return
        out, _ = QFileDialog.getSaveFileName(
            self,
            "Export Selected CSV",
            f"History_{payload.get('invoiceNumber', 'Invoice')}.csv",
            "CSV Files (*.csv)"
        )
        if not out:
            return
        self.exportInvoiceCSV(out, payload)
        QMessageBox.information(self, "Done", f"Invoice CSV exported to {out}")
    
    def number_to_words(self, num):
        # Simple number to words conversion for amounts
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine']
        teens = ['Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        if num == 0:
            return 'Zero'
        
        def convert_hundreds(n):
            result = ''
            if n >= 100:
                result += ones[n // 100] + ' Hundred '
                n %= 100
            if n >= 20:
                result += tens[n // 10] + ' '
                n %= 10
            elif n >= 10:
                result += teens[n - 10] + ' '
                n = 0
            if n > 0:
                result += ones[n] + ' '
            return result
        
        if num < 1000:
            return convert_hundreds(num).strip()
        elif num < 100000:
            thousands = num // 1000
            remainder = num % 1000
            result = convert_hundreds(thousands) + 'Thousand '
            if remainder > 0:
                result += convert_hundreds(remainder)
            return result.strip()
        else:
            return 'Amount too large'



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InvoiceWriter()
    window.show()
    sys.exit(app.exec_())
