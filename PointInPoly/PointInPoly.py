# -*- coding: utf-8 -*-

# import os
from AngleUtil.AngleUtil import *
import math


class CalcAngle:
    def __init__(self):
        pass

    @staticmethod
    def calc(point_a, point_b):
        A = MyLatLng(long_lat=point_a)
        B = MyLatLng(long_lat=point_b)
        return AngleUtil.get_radius(A, B)

    @staticmethod
    def calc2(internal_point_1, internal_point_2, point):
        angle1 = CalcAngle.calc(internal_point_1, internal_point_2)
        angle1 = CalcAngle.calc(internal_point_1, internal_point_2)

class Poly:
	def __init__(self, point_list):
		self.point_list = point_list

	def point_in_poly(self, point):
		pass


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
    ca = CalcAngle()
    poly = Poly(plist)
    result = poly.point_in_poly(point)
    print result
