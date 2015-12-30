import time
import sys
import numpy as np
from scipy.spatial import distance
import matplotlib as mpl
mpl.use('Qt5Agg')
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.ticker import NullLocator
from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout,
                             QVBoxLayout, QPushButton)
from PyQt5 import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.delay_nn = 0.5
        self.delay_opt2 = 0.5
        self.init_ui()
        self.show()

    def init_ui(self):
        self.setWindowTitle('TSP')
        self.setGeometry(100, 100, 1500, 1000)
        self.canvas = CityMap(self)
        self.button1 = QPushButton('Clear all')
        self.button1.clicked.connect(self.clear_fig)
        self.button2 = QPushButton('Nearest neighbor method')
        self.button2.clicked.connect(self.exec_nn)
        self.button3 = QPushButton('2-opt method')
        self.button3.setEnabled(False)
        self.layout1 = QVBoxLayout()
        self.layout1.addWidget(self.canvas)
        self.layout_button = QHBoxLayout()
        self.layout_button.addWidget(self.button1)
        self.layout_button.addWidget(self.button2)
        self.layout_button.addWidget(self.button3)
        self.layout1.addLayout(self.layout_button)
        self.setLayout(self.layout1)

    def clear_fig(self):
        self.canvas.clear_all()
        self.button2.setEnabled(True)
        self.button3.setEnabled(False)

    def exec_nn(self):
        self.canvas.nearest_neighbor(self.delay_nn)
        self.button2.setEnabled(False)
        self.button3.setEnabled(True)

class CityMap(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.num_city = None
        self.city_pos = None
        self.dist_table = None
        self.path = None
        self.fig = plt.figure()
        super(CityMap, self).__init__(self.fig)
        self.setParent(parent)
        self.init_axes()
        self.connect()

    def init_axes(self):
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(0.0, 1.0)
        self.ax.set_ylim(0.0, 1.0)
        self.ax.set_aspect('equal')
        self.ax.xaxis.set_major_locator(NullLocator())
        self.ax.yaxis.set_major_locator(NullLocator())

    def put_city(self, event):
        if event.inaxes != self.ax: return
        if event.button != 1: return
        x = event.xdata
        y = event.ydata
        self.ax.plot(x, y, 'bo', markersize=10, picker=5)
        self.draw()

    def remove_city(self, event):
        mouseevent = event.mouseevent
        if mouseevent.button != 3: return
        thisline = event.artist
        thisline.remove()
        self.draw()

    def getx(self):
        lines = self.ax.lines
        return np.array([line.get_xdata() for line in lines]).flatten()

    def gety(self):
        lines = self.ax.lines
        return np.array([line.get_ydata() for line in lines]).flatten()

    def clear_dots(self, event=False):
        if not event: return
        if event.inaxes != self.ax: return
        if event.button != 2: return
        self.clear_all()

    def clear_all(self):
        self.unfix_instance()
        self.ax.cla()
        self.init_axes()
        self.draw()

    def fix_instance(self):
        self.num_city = len(self.ax.lines)
        X = self.getx()
        Y = self.gety()
        self.city_pos = np.vstack((X, Y)).transpose()
        self.dist_table = distance.cdist(self.city_pos, self.city_pos)
        self.path = np.array(range(self.num_city))
        self.disconnect()

    def unfix_instance(self):
        self.num_city = None
        self.city_pos = None
        self.dist_table = None
        self.path = None
        self.connect()

    def connect(self):
        self.cid_putdot = self.fig.canvas.mpl_connect('button_press_event', self.put_city)
        self.cid_remove = self.fig.canvas.mpl_connect('pick_event', self.remove_city)
        self.cid_clear = self.fig.canvas.mpl_connect('button_press_event', self.clear_dots)

    def disconnect(self):
        self.fig.canvas.mpl_disconnect(self.cid_putdot)
        self.fig.canvas.mpl_disconnect(self.cid_remove)
        self.fig.canvas.mpl_disconnect(self.cid_clear)

    def nearest_neighbor(self, delay=0.0):
        self.fix_instance()
        for frame in range(self.num_city):
            if frame < self.num_city - 1:
                current_city = self.path[frame]
                remain_city = self.path[frame+1:]
                remain_distance = np.take(self.dist_table[current_city], remain_city)
                min_pos = np.argmin(remain_distance)
                self.path[frame+1], remain_city[min_pos] = remain_city[min_pos], self.path[frame+1]
                self.plot_line_between_cities(current_city, self.path[frame+1])
                self.draw()
                self.fig.canvas.flush_events()
                time.sleep(delay)
                self.ax.lines[-1].set_color('b')
                self.draw()
            else:
                self.plot_line_between_cities(self.path[frame], self.path[0])
                self.draw()
                self.fig.canvas.flush_events()
                time.sleep(delay)
                self.ax.lines[-1].set_color('b')
                self.draw()

    def plot_line_between_cities(self, cind1, cind2, style='r-'):
        city1 = self.city_pos[cind1]
        city2 = self.city_pos[cind2]
        self.ax.plot([city1[0], city2[0]], [city1[1], city2[1]], style)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
