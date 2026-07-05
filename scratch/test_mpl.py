import sys
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5.QtWidgets import QApplication, QMainWindow

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

app = QApplication(sys.argv)
win = QMainWindow()
fig = Figure()
canvas = FigureCanvas(fig)
win.setCentralWidget(canvas)
print("SUCCESS!")
