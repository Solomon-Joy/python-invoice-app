import sys
import os
import urllib.parse
from database import DatabaseManager, migrate_from_json
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from collections import defaultdict
print("Imports successful")
