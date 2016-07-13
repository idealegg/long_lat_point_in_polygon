# -*- coding: utf-8 -*-

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from AngleUtil.AngleUtil import Rj

class DrawCoordinateGraph:
    def __init__(self, point_list, special_point):
        self.point_list = point_list
        self.special_point = special_point

    def draw_graph(self):
        fig = plt.figure()
        ax = Axes3D(fig)
        X = np.array(map(lambda(x): x[0], self.point_list))
        Y = np.array(map(lambda(x): x[1], self.point_list))
        X, Y = np.meshgrid(X, Y)
        #Z = np.array(map(lambda(x): x[2], self.point_list))
        Z = np.sqrt(Rj**2 - X**2 - Y**2)

        # 具体函数方法可用 help(function) 查看，如：help(ax.plot_surface)
        ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='rainbow')

        plt.show()

if __name__ == '__main__':
    point_list = [(1,2,3), (4,5,6), (7,8,9)]
    special_point = (2, 2, 3)
    dcg = DrawCoordinateGraph(point_list, special_point)
    dcg.draw_graph()
