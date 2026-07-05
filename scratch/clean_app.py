import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Remove all debug prints at top
debug_top = """import sys
print("Imported sys")
import csv
import json
print("Imported json")
import os
print("Imported os")
import urllib.parse
print("Imported urllib")
from database import DatabaseManager, migrate_from_json
print("Imported database")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import defaultdict
import webbrowser"""

clean_top = """import sys
import csv
import json
import os
import urllib.parse
from database import DatabaseManager, migrate_from_json
import webbrowser"""

content = content.replace(debug_top, clean_top)

# 2. Make sure createDashboardTab has the imports
dash_target = """    def createDashboardTab(self):
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure"""
if dash_target not in content:
    old_dash = """    def createDashboardTab(self):"""
    content = content.replace(old_dash, dash_target)

# 3. Clean up the try-except at the bottom
debug_bottom = """if __name__ == '__main__':
    print("Starting app...")
    try:
        app = QApplication(sys.argv)
        print("QApplication created.")
        window = InvoiceWriter()
        print("InvoiceWriter created.")
        window.show()
        print("Window shown.")
        sys.exit(app.exec_())
    except Exception as e:
        print("Caught exception:", e)
        import traceback
        with open("crash.log", "w") as f:
            traceback.print_exc(file=f)"""

clean_bottom = """if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InvoiceWriter()
    window.show()
    sys.exit(app.exec_())"""

content = content.replace(debug_bottom, clean_bottom)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
