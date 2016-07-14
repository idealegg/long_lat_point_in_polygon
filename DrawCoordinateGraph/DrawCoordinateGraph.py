# -*- coding: utf-8 -*-

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from AngleUtil.AngleUtil import Rj, Rc
import pprint


def get_data_list(data1, data2):
    #tmp_x_array = np.array([data1, data2])
    #return np.linspace(tmp_x_array.min(), tmp_x_array.max(), 10)
    return np.linspace(data1, data2, 100)


class DrawCoordinateGraph:
    def __init__(self, point_list, special_point):
        self.point_list = point_list
        self.special_point = special_point

    def get_data_set(self, mode, has_x=False):
        X = np.array([])
        Y = np.array([])
        Z = np.array([])
        if mode == 'point':
            if has_x:
                X = np.array(map(lambda (x): x[0], self.point_list))
            else:
                X = np.array(map(lambda (x): 0, self.point_list))
            Y = np.array(map(lambda (x): x[1], self.point_list))
            # X, Y = np.meshgrid(X, Y)
            Z = np.array(map(lambda (x): x[2], self.point_list))
        elif mode == 'line':
            for index in range(len(self.point_list)):
                p1 = self.point_list[index]
                if index == len(self.point_list)-1:
                    p2 = self.point_list[0]
                else:
                    p2 = self.point_list[index+1]
                if has_x:
                    X = np.append(X, get_data_list(p1[0], p2[0]))
                else:
                    X = np.append(X, get_data_list(0., 0.))
                if p1[0] == p2[0] or not has_x:
                    Y = np.append(Y, get_data_list(p1[1], p2[1]))
                    if p1[1] == p2[1]:
                        Z = np.append(Z, get_data_list(p1[2], p2[2]))
                    else:
                        #Z = p2[2]-(p2[2]-p1[2])*(p2[1]-Y)/(p2[1]-p1[1])
                        Z = Rj*np.sqrt(np.abs(Rc**2-X**2-Y**2))/Rc
                else:
                    Y = np.append(Y, get_data_list(p1[1], p2[1]))
                    #Y = p2[1]-(p2[1] - p1[1]) * (p2[0] - X) / (p2[0] - p1[0])
                    #Z = p2[2]-(p2[2] - p1[2]) * (p2[0] - X) / (p2[0] - p1[0])
                    Z = Rj*np.sqrt(np.abs(Rc**2-X**2-Y**2))/Rc
        return X, Y, Z

    def draw_graph(self, mode='line', has_x=True):
        fig = plt.figure()
        ax = Axes3D(fig)
        X, Y, Z = self.get_data_set(mode, has_x)

        # 具体函数方法可用 help(function) 查看，如：help(ax.plot_surface)
        #ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='rainbow')
        ax.set_xlim(left=min(X.min(), self.special_point[0])
                    , right=max(X.max(), self.special_point[0]))
        ax.set_ylim(bottom=min(Y.min(), self.special_point[1])
                    , top=max(Y.max(), self.special_point[1]))
        ax.set_zlim(bottom=min(Z.min(), self.special_point[2])
                    , top=max(Z.max(), self.special_point[2]))

        plt.title('title')
        #显示坐标轴标示
        plt.xlabel('x')
        plt.ylabel('y')

        '''
        print "point_list:\n"
        pprint.pprint(self.point_list)
        print "special point:\n"
        pprint.pprint(self.special_point)
        print "X: %d\n" % X.size
        pprint.pprint(X.tolist())
        print "Y: %d\n" % Y.size
        pprint.pprint(Y.tolist())
        print "Z: %d\n" % Z.size
        pprint.pprint(Z.tolist())
        '''
        ax.scatter(X, Y, Z, c='r')  # 绘点
        if has_x:
            ax.scatter(np.array([self.special_point[0]]), np.array([self.special_point[1]]),
                   np.array([self.special_point[2]]), c='g')
        else:
            ax.scatter(0, np.array([self.special_point[1]]),
                   np.array([self.special_point[2]]), c='g')
        plt.show()

if __name__ == '__main__':
    point_list = [(1,2,3), (4,5,6), (7,8,9)]
    special_point = (2, 2, 3)
    dcg = DrawCoordinateGraph(point_list, special_point)
    dcg.draw_graph()
