import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

classes_code = """
class UpperLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.force_upper)

    def force_upper(self, text):
        upper_text = text.upper()
        if text != upper_text:
            pos = self.cursorPosition()
            self.blockSignals(True)
            self.setText(upper_text)
            self.blockSignals(False)
            self.setCursorPosition(pos)

class UpperTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textChanged.connect(self.force_upper)

    def force_upper(self):
        text = self.toPlainText()
        upper_text = text.upper()
        if text != upper_text:
            cursor = self.textCursor()
            pos = cursor.position()
            self.blockSignals(True)
            self.setPlainText(upper_text)
            self.blockSignals(False)
            cursor.setPosition(pos)
            self.setTextCursor(cursor)

class InvoiceWriter(QMainWindow):"""

content = content.replace("class InvoiceWriter(QMainWindow):", classes_code)

# Only replace QLineEdit( and QTextEdit( instantiations
# Be careful not to replace isinstance(field, QLineEdit)
content = re.sub(r'([ =])QLineEdit\(', r'\1UpperLineEdit(', content)
content = re.sub(r'([ =])QTextEdit\(', r'\1UpperTextEdit(', content)

# Except for gstLivePreview which we might not care, but it's fine
# And the logo setting should probably stay normal QLineEdit just in case
content = content.replace("UpperLineEdit(self.db.get_setting('COMPANY_LOGO'", "QLineEdit(self.db.get_setting('COMPANY_LOGO'")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
