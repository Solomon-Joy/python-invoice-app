import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Add Settings to initUI tabs
old_init_tabs = """        self.historyTab = self.createHistoryTab()

        self.tabs.addTab(self.gstTab, "GST Invoice")
        self.tabs.addTab(self.normalTab, "Standard Invoice")"""

new_init_tabs = """        self.historyTab = self.createHistoryTab()
        self.settingsTab = self.createSettingsTab()

        self.tabs.addTab(self.gstTab, "GST Invoice")
        self.tabs.addTab(self.normalTab, "Standard Invoice")
        self.tabs.addTab(self.settingsTab, "Settings")"""

content = content.replace(old_init_tabs, new_init_tabs)

# Add createSettingsTab function
settings_func = """    def createSettingsTab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        group = self.createSection("Company Details")
        form = QFormLayout()

        self.settingCompanyName = QLineEdit(self.db.get_setting('COMPANY_NAME', self.COMPANY_NAME))
        self.settingCompanyAddress = QLineEdit(self.db.get_setting('COMPANY_ADDRESS', self.COMPANY_ADDRESS))
        self.settingCompanyPhone = QLineEdit(self.db.get_setting('COMPANY_PHONE', self.COMPANY_PHONE))
        self.settingCompanyGSTIN = QLineEdit(self.db.get_setting('COMPANY_GSTIN', self.COMPANY_GSTIN))
        self.settingCompanyPAN = QLineEdit(self.db.get_setting('COMPANY_PAN', ''))
        self.settingCompanyFSSAI = QLineEdit(self.db.get_setting('COMPANY_FSSAI', ''))
        
        logo_layout = QHBoxLayout()
        self.settingCompanyLogo = QLineEdit(self.db.get_setting('COMPANY_LOGO', ''))
        self.settingCompanyLogo.setReadOnly(True)
        btn_logo = QPushButton("Browse")
        btn_logo.clicked.connect(self.browseLogo)
        logo_layout.addWidget(self.settingCompanyLogo)
        logo_layout.addWidget(btn_logo)

        form.addRow("Company Name", self.settingCompanyName)
        form.addRow("Address", self.settingCompanyAddress)
        form.addRow("Phone", self.settingCompanyPhone)
        form.addRow("GSTIN", self.settingCompanyGSTIN)
        form.addRow("PAN", self.settingCompanyPAN)
        form.addRow("FSSAI", self.settingCompanyFSSAI)
        form.addRow("Logo Path", logo_layout)

        group['layout'].addLayout(form)
        layout.addWidget(group['widget'])

        saveBtn = QPushButton("Save Settings")
        saveBtn.setObjectName("primary")
        saveBtn.clicked.connect(self.saveSettings)
        layout.addWidget(saveBtn)
        layout.addStretch()

        return widget

    def browseLogo(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)", options=options)
        if fileName:
            self.settingCompanyLogo.setText(fileName)

    def saveSettings(self):
        self.db.set_setting('COMPANY_NAME', self.settingCompanyName.text().strip())
        self.db.set_setting('COMPANY_ADDRESS', self.settingCompanyAddress.text().strip())
        self.db.set_setting('COMPANY_PHONE', self.settingCompanyPhone.text().strip())
        self.db.set_setting('COMPANY_GSTIN', self.settingCompanyGSTIN.text().strip())
        self.db.set_setting('COMPANY_PAN', self.settingCompanyPAN.text().strip())
        self.db.set_setting('COMPANY_FSSAI', self.settingCompanyFSSAI.text().strip())
        self.db.set_setting('COMPANY_LOGO', self.settingCompanyLogo.text().strip())
        QMessageBox.information(self, "Success", "Settings saved successfully!")

"""

# Insert before createHistoryTab
target = "    def createHistoryTab(self):"
if settings_func not in content:
    content = content.replace(target, settings_func + target)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
