import numpy as np
import scipy as sp
from scipy.spatial import distance
import matplotlib as mpl
import matplotlib.pyplot as plt


def main():
    city_pos = np.loadtxt('city_location/example1.dat')
    dist_table = distance.cdist(city_pos, city_pos)
    plot_path(city_pos)
    # Initial guess with the nearest neighbor method
    path = nearest_neighbor(dist_table)
    plot_path(city_pos, path)
    print('total dist: {0}'.format(calc_total_dist(dist_table, path)))
    # Refine the initial guess
    opt_2(dist_table, path)
    plot_path(city_pos, path)
    print('total dist: {0}'.format(calc_total_dist(dist_table, path)))


def nearest_neighbor(distance_table):
    '''Return initial path generated by the nearest-neighvor method

    Parameters
    ----------
    city_pos : array_like
        2d array of city positions

    Returns
    -------
    path : array_like
        1d array of initial guess of path
    '''
    size = distance_table.shape[0]
    path = np.array(range(size))
    for i in range(size-1):
        current_city = path[i]
        remain_city = path[i+1:]
        remain_distance = np.take(distance_table[current_city], remain_city)
        min_pos = np.argmin(remain_distance)
        path[i+1], remain_city[min_pos] = remain_city[min_pos], path[i+1]
    return path


def opt_2(distance_table, path):
    '''Improve path with the 2-opt method.

    Parameters
    ----------
    distance_table : array_like
        2d array whose elements represents distances between cities

    path : array_like
        1d array representing the order of route
    '''
    size = path.shape[0]
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
                    l1 = distance_table[path[i], path[i1]]
                    l2 = distance_table[path[j], path[j1]]
                    l3 = distance_table[path[i], path[j]]
                    l4 = distance_table[path[i1], path[j1]]
                    if l1 + l2 > l3 + l4:
                        new_path = path[i1:j+1]
                        path[i1:j+1] = new_path[::-1]
                        count += 1
        if count == 0: break
    return 0


def calc_total_dist(distance_table, path):
    '''Calculate total distance of path

    Parameters
    ----------
    distance_table : array_like
        2d array of distances between cities

    path : array_like
        1d array of path

    Returns
    -------
    float
        Total distance of `path`
    '''
    size = path.shape[0]
    sum = 0.0
    for i in range(size):
        if i == size - 1:
            i1 = 0
        else:
            i1 = i + 1
        sum += distance_table[path[i], path[i1]]
    return sum


def plot_path(city_pos, path=None):
    '''Plot path

    Parameters
    ---------
    city_pos : array_like
        2d array of city positions

    path : array_like
        1d array representing path
    '''
    plt.xlim(0.0, 1.0)
    plt.ylim(0.0, 1.0)
    if path is not None:
        len = path.shape[0]
        for i in range(len):
            if i == len - 1:
                i1 = 0
            else:
                i1 = i + 1
            city1 = city_pos[path[i]]
            city2 = city_pos[path[i1]]
            plt.plot([city1[0], city2[0]], [city1[1], city2[1]], "k-", lw=2)
    plt.plot(city_pos[0,0], city_pos[0,1], "ro", markersize=10)
    plt.plot(city_pos[1:,0], city_pos[1:,1], "o", markersize=10)
    plt.gca().set_aspect('equal')
    plt.show()


if __name__ == '__main__':
    main()