import time
import sys
import numpy as np
import matplotlib as mpl
mpl.use('Qt4Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from PyQt4.QtGui import (QApplication, QWidget, QHBoxLayout,
                         QVBoxLayout, QGridLayout, QPushButton, QLabel,
                         QLineEdit)
from PyQt4.QtGui import QDoubleValidator
import PyQt4.QtCore as QtCore


class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.delay_nn = 0.0
        self.delay_opt2 = 0.0
        self.init_ui()
        self.show()

    def init_ui(self):
        self.setWindowTitle('TSP')
        self.setGeometry(50, 50, 1200, 800)
        self.canvas = CityMap(self)
        self.canvas.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.button1 = QPushButton('Clear all')
        self.button1.clicked.connect(self.clear_fig)
        self.button2 = QPushButton('Nearest neighbor method')
        self.button2.clicked.connect(self.exec_nn)
        self.button3 = QPushButton('2-opt method')
        self.button3.clicked.connect(self.exec_opt2)
        self.button3.setEnabled(False)
        self.button4 = QPushButton('Clear route')
        self.button4.setEnabled(False)
        self.button4.clicked.connect(self.clear_route)
        self.label1 = QLabel('Delay (sec)')
        self.label2 = QLabel('Delay (sec)')
        self.delaytime1 = QLineEdit()
        self.delaytime1.setValidator(QDoubleValidator(0.0, 2.0, 3))
        self.delaytime2 = QLineEdit()
        self.delaytime2.setValidator(QDoubleValidator(0.0, 2.0, 3))
        self.layout1 = QVBoxLayout()
        self.layout1.addWidget(self.canvas)
        self.grid = QGridLayout()
        self.grid.addWidget(self.button1, 0, 0)
        self.grid.addWidget(self.button2, 0, 1)
        self.grid.addWidget(self.button3, 0, 2)
        self.grid.addWidget(self.button4, 1, 0)
        self.box1 = QHBoxLayout()
        self.box2 = QHBoxLayout()
        self.box1.addWidget(self.label1)
        self.box1.addWidget(self.delaytime1)
        self.box2.addWidget(self.label2)
        self.box2.addWidget(self.delaytime2)
        self.grid.addLayout(self.box1, 1, 1)
        self.grid.addLayout(self.box2, 1, 2)
        self.layout1.addLayout(self.grid)
        self.setLayout(self.layout1)

    def clear_fig(self):
        self.canvas.clear_all()
        self.button2.setEnabled(True)
        self.button3.setEnabled(False)
        self.button4.setEnabled(False)

    def clear_route(self):
        self.canvas.clear_route()
        self.button2.setEnabled(True)
        self.button3.setEnabled(False)

    def exec_nn(self):
        delaytime = self.delaytime1.text()
        if delaytime == '':
            self.delay_nn = 0.0
        else:
            self.delay_nn = float(delaytime)
        self.canvas.nearest_neighbor(self.delay_nn)
        self.button2.setEnabled(False)
        self.button3.setEnabled(True)
        self.button4.setEnabled(True)

    def exec_opt2(self):
        delaytime = self.delaytime2.text()
        if delaytime == '':
            self.delay_opt2 = 0.0
        else:
            self.delay_opt2 = float(delaytime)
        self.canvas.opt2(self.delay_opt2)
        self.button3.setEnabled(False)


class CityMap(FigureCanvasQTAgg):
    def __init__(self, parent=None):
        self.num_city = None
        self.city_pos = None
        self.dist_table = None
        self.path = None
        self.init_dist = None
        self.current_dist = None
        self.is_shift_held = False
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
        self.dist_text = self.ax.text(1.01, 1.0,
                                      'Initial distance\n\n\nCurrent distance\n',
                                      va='top')

    def on_shift_press(self, event):
        if event.key == 'shift':
            self.is_shift_held = True

    def on_shift_release(self, event):
        if event.key == 'shift':
            self.is_shift_held = False

    def put_city(self, event):
        if event.inaxes != self.ax: return
        if event.button != 1 or self.is_shift_held:
            return
        x = event.xdata
        y = event.ydata
        self.ax.plot(x, y, 'bo', markersize=10, picker=7)
        self.ax.lines[0].set_color('r')
        self.draw()

    def remove_city(self, event):
        mouseevent = event.mouseevent
        if mouseevent.button != 3: return
        thisline = event.artist
        thisline.remove()
        if len(self.ax.lines) != 0:
            self.ax.lines[0].set_color('r')
        self.draw()

    def select_init_city(self, event):
        mouseevent = event.mouseevent
        if mouseevent.button != 1 or\
           not self.is_shift_held:
            return
        thisline = event.artist
        self.ax.lines.remove(thisline)
        self.ax.lines[0].set_color('b')
        self.ax.lines.insert(0, thisline)
        self.ax.lines[0].set_color('r')
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

    def clear_route(self):
        if self.num_city is not None:
            for line in self.ax.lines[self.num_city:]:
                line.remove()
            self.draw()
            self.unfix_instance()

    def fix_instance(self):
        self.disconnect()
        self.num_city = len(self.ax.lines)
        X = self.getx()
        Y = self.gety()
        self.city_pos = np.vstack((X, Y)).transpose()
        self.dist_table = get_dist_table(self.city_pos)
        self.path = np.array(range(self.num_city))

    def unfix_instance(self):
        self.connect()
        self.num_city = None
        self.city_pos = None
        self.dist_table = None
        self.path = None
        self.init_dist = None
        self.current_dist = None

    def connect(self):
        self.cid_putdot = self.fig.canvas.mpl_connect('button_press_event', self.put_city)
        self.cid_remove = self.fig.canvas.mpl_connect('pick_event', self.remove_city)
        self.cid_clear = self.fig.canvas.mpl_connect('button_press_event', self.clear_dots)
        self.cid_press_shift = self.fig.canvas.mpl_connect('key_press_event', self.on_shift_press)
        self.cid_release_shift = self.fig.canvas.mpl_connect('key_release_event', self.on_shift_release)
        self.cid_select_init = self.fig.canvas.mpl_connect('pick_event', self.select_init_city)

    def disconnect(self):
        self.fig.canvas.mpl_disconnect(self.cid_putdot)
        self.fig.canvas.mpl_disconnect(self.cid_remove)
        self.fig.canvas.mpl_disconnect(self.cid_clear)
        self.fig.canvas.mpl_disconnect(self.cid_press_shift)
        self.fig.canvas.mpl_disconnect(self.cid_release_shift)
        self.fig.canvas.mpl_disconnect(self.cid_select_init)

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
        self.init_dist = self.calc_total_dist()
        self.update_distance_displayed()

    def plot_line_between_cities(self, cind1, cind2, style='r-'):
        city1 = self.city_pos[cind1]
        city2 = self.city_pos[cind2]
        line, = self.ax.plot([city1[0], city2[0]], [city1[1], city2[1]], style)
        return line

    def opt2(self, delay=0.0):
        size = self.num_city
        while True:
            count = 0
            for i in range(size-2):
                i1 = i + 1
                for j in range(i+2, size):
                    if j == size - 1:
                        j1 = 0
                    else:
                        j1 = j + 1
                    if i != 0 or j1 != 0:
                        l1 = self.dist_table[self.path[i], self.path[i1]]
                        l2 = self.dist_table[self.path[j], self.path[j1]]
                        l3 = self.dist_table[self.path[i], self.path[j]]
                        l4 = self.dist_table[self.path[i1], self.path[j1]]
                        if l1 + l2 > l3 + l4:
                            lines = self.ax.lines[self.num_city::]
                            l1_lobj = self.get_matching_path(lines, self.path[i], self.path[i1])
                            l2_lobj = self.get_matching_path(lines, self.path[j], self.path[j1])
                            l1_lobj.set_color('r')
                            l2_lobj.set_color('r')
                            self.draw()
                            self.fig.canvas.flush_events()
                            new_path = self.path[i1:j+1]
                            self.path[i1:j+1] = new_path[::-1]
                            time.sleep(delay/2.0)
                            l1_lobj.remove()
                            l2_lobj.remove()
                            line1 = self.plot_line_between_cities(self.path[i], self.path[i1], style='r-')
                            line2 = self.plot_line_between_cities(self.path[j], self.path[j1], style='r-')
                            self.draw()
                            self.fig.canvas.flush_events()
                            time.sleep(delay/2.0)
                            line1.set_color('b')
                            line2.set_color('b')
                            self.draw()
                            self.fig.canvas.flush_events()
                            count += 1
            if count == 0: break
        self.current_dist = self.calc_total_dist()
        self.update_distance_displayed()

    def get_matching_path(self, lines, cind1, cind2):
        city1_cood = self.city_pos[cind1]
        city2_cood = self.city_pos[cind2]
        path_data = np.vstack((city1_cood, city2_cood))
        for line in lines:
            line_data = line.get_xydata()
            if np.array_equal(path_data, line_data) or\
               np.array_equal(path_data, line_data[::-1, ...]):
                return line

    def calc_total_dist(self):
        size = self.num_city
        sum = 0.0
        for i in range(size):
            if i == size - 1:
                i1 = 0
            else:
                i1 = i + 1
            sum += self.dist_table[self.path[i], self.path[i1]]
        return sum

    def update_distance_displayed(self):
        if self.init_dist is not None:
            if self.current_dist is not None:
                self.dist_text.set_text('Initial distance\n{0:.4f}\n\n'\
                                        'Current distance\n{1:.4f}'\
                                        .format(self.init_dist, self.current_dist))
            else:
                self.dist_text.set_text('Initial distance\n{0:.4f}\n\n'\
                                        'Current distance\n'\
                                        .format(self.init_dist))
            self.draw()


def get_dist_table(city_pos):
    return np.sqrt(((city_pos[:,np.newaxis] - city_pos)**2).sum(axis=2))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
