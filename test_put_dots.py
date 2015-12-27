import numpy as np
import matplotlib as mpl
from matplotlib.ticker import NullLocator
import matplotlib.pyplot as plt

def main():
    citymap = CityMap()
    print(citymap.xdata)
    print(citymap.ydata)
    return 0


class CityMap:
    def __init__(self):
        self.xdata = []
        self.ydata = []
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlim(0.0, 1.0)
        self.ax.set_ylim(0.0, 1.0)
        self.ax.set_aspect('equal')
        self.ax.xaxis.set_major_locator(NullLocator())
        self.ax.yaxis.set_major_locator(NullLocator())
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.put_city)
        plt.show()

    def put_city(self, event):
        if event.inaxes != self.ax: return
        x = event.xdata
        y = event.ydata
        self.xdata.append(x)
        self.ydata.append(y)
        self.ax.plot(x, y, 'bo', markersize=10)
        plt.draw()


if __name__ == '__main__':
    main()
