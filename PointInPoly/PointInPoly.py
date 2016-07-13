# -*- coding: utf-8 -*-

# import os
from AngleUtil.AngleUtil import *
from DrawCoordinateGraph.DrawCoordinateGraph import *
import math


class Poly:
    def __init__(self, point_list):
        self.point_list = point_list
        self.coordinate_point_list = []

    def point_in_poly(self, point):
        o_point = MyLatLng(long_lat=point)
        sum = 0
        length = len(self.point_list)
        for index in range(length):
            i_point_1 = MyLatLng(long_lat=self.point_list[index])
            if index == length - 1:
                i_point_2 = MyLatLng(long_lat=self.point_list[0])
            else:
                i_point_2 = MyLatLng(long_lat=self.point_list[index+1])
            sum += AngleUtil.get_3_points_radius(i_point_1, i_point_2, o_point)
        return math.fabs(sum - math.pi * 2) < math.pi * 0.5

    def fill_coordinate_point_list(self):
        original_point = MyLatLng(0,0)
        for point in self.point_list:
            point_item = MyLatLng(long_lat=point)
            self.coordinate_point_list.append(AngleUtil.get_vector(point_item, original_point))

    def draw_graph(self):
        self.fill_coordinate_point_list()
        dcg = DrawCoordinateGraph(self.coordinate_point_list, (0,0,0))
        dcg.draw_graph()


if __name__ == '__main__':
    tmp='''
    CX128 CX296 CX15 CX16 CX171 CX170 CX130 CX169 CX168 CX167 CX166 CX165 CX161 CX162 CX163 CX164 CX128

CX15    |  292300N1130712E    |
CX16    |  290200N1143400E    |
CX128    |  292500N1121000E    |  -------An xiang
CX130    |  265430N1123800E    |
CX150    |  251226N1133810E    |
CX151    |  244803N1145051E    |
CX152    |  244115N1130000E    |
CX153    |  241737N1125557E    |
CX154    |  235104N1124743E    |
CX155    |  261332N1134323E    |
CX156    |  262210N1135357E    |
CX157    |  262414N1140132E    |
CX160    |  275257N1092121E    |
CX161    |  281906N1114720E    |
CX162    |  282629N1115540E    |
CX163    |  283007N1120434E    |
CX164    |  283100N1121144E    |
CX165    |  280947N1114249E    |
CX166    |  275805N1114253E    |
CX167    |  274810N1114758E    |
CX168    |  274111N1115624E    |
CX169    |  273718N1121729E    |
CX170    |  273742N1133142E    |
CX171    |  274501N1141326E    |
CX296    |  292401N1123904E    |

    '''
    CX15 = '292300N1130712E'
    CX16 = '290200N1143400E'
    CX128 = '292500N1121000E'
    CX130 = '265430N1123800E'
    CX150 = '251226N1133810E'
    CX151 = '244803N1145051E'
    CX152 = '244115N1130000E'
    CX153 = '241737N1125557E'
    CX154 = '235104N1124743E'
    CX155 = '261332N1134323E'
    CX156 = '262210N1135357E'
    CX157 = '262414N1140132E'
    CX160 = '275257N1092121E'
    CX161 = '281906N1114720E'
    CX162 = '282629N1115540E'
    CX163 = '283007N1120434E'
    CX164 = '283100N1121144E'
    CX165 = '280947N1114249E'
    CX166 = '275805N1114253E'
    CX167 = '274810N1114758E'
    CX168 = '274111N1115624E'
    CX169 = '273718N1121729E'
    CX170 = '273742N1133142E'
    CX171 = '274501N1141326E'
    CX296 = '292401N1123904E'
    plist = (CX128,CX296,CX15,CX16,CX171,CX170,CX130,CX169,CX168,CX167,CX166,CX165,CX161,CX162,CX163,CX164,CX128)
    poly = Poly(plist)
    result = poly.point_in_poly('281332N1142106E')
    print result
    poly.draw_graph()

