import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

bad_imports = """from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
print("Imported FigureCanvas")
from matplotlib.figure import Figure
print("Imported Figure")
from collections import defaultdict
print("Imported defaultdict")"""

content = content.replace(bad_imports, "")

good_imports = """from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import defaultdict
"""

content = content.replace("from PyQt5.QtPrintSupport import QPrinter, QPrintDialog", good_imports)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)
