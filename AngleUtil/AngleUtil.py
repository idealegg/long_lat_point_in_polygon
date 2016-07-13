# -*- coding: utf-8 -*-
import math
import numpy
Rc = 6378137
Rj = 6356725
point_list = []

class MyLatLng:
    def __init__(self, longitude=0, latitude=0, long_lat="", mode=1):
        self.m_LoDeg = 0
        self.m_LoMin = 0
        self.m_LoSec = 0

        self.m_LaDeg = 0
        self.m_LaMin = 0
        self.m_LaSec = 0

        self.m_Longitude = 0.
        self.m_Latitude = 0.
        self.m_Rad_lo = 0.
        self.m_Rad_la = 0.
        self.Ec = 0.
        self.Ed = 0.
        if not long_lat:
            self.init1(longitude, latitude)
        else:
            self.init2(long_lat)

    def init1(self, longitude, latitude):
        self.m_LoDeg = int(longitude)
        self.m_LoMin = int((longitude-self.m_LoDeg)*60)
        self.m_LoSec = int((longitude-self.m_LoDeg-self.m_LoMin/60.0)*3600)

        self.m_LaDeg = int(latitude)
        self.m_LaMin = int((latitude-self.m_LaDeg)*60)
        self.m_LaSec = int((latitude-self.m_LaDeg-self.m_LaMin/60.)*3600)

        self.m_Longitude = longitude
        self.m_Latitude = latitude
        self.m_Rad_lo = longitude*math.pi/180.
        self.m_Rad_la = latitude*math.pi/180.
        self.Ec = Rj+(Rc-Rj)*(90.-self.m_Latitude)/90.
        self.Ed = self.Ec*math.cos(self.m_Rad_la)

    def init2(self, long_lat):
        self.m_L0Deg = int(long_lat[7:10])
        self.m_LoMin = int(long_lat[10:12])
        self.m_LoSec = int(long_lat[12:14])

        self.m_LaDeg = int(long_lat[:2])
        self.m_LaMin = int(long_lat[2:4])
        self.m_LaSec = int(long_lat[4:6])

        self.m_Longitude = (self.m_LoSec / 60. + self.m_LoMin) / 60. + self.m_LoDeg
        self.m_Latitude = (self.m_LaSec / 60. + self.m_LaMin) / 60. + self.m_LaDeg
        self.m_Rad_lo = self.m_Longitude * math.pi / 180.
        self.m_Rad_la = self.m_Latitude * math.pi / 180.
        self.Ec = Rj + (Rc - Rj) * (90. - self.m_Latitude) / 90.
        self.Ed = self.Ec * math.cos(self.m_Rad_la)


class AngleUtil:
    '''
	/**
	 * 求B点经纬度	 * @param A 已知点的经纬度，
	 * @param distance   AB两地的距离  单位km
	 * @param angle  AB连线与正北方向的夹角（0~360）
	 * @return  B点的经纬度
	 */
    '''
    def __init__(self):
        pass

    @staticmethod
    def get_my_lat_lng(point_a, distance, angle):

        dx = distance*1000*math.sin(math.radians(angle))
        dy= distance*1000*math.cos(math.radians(angle))

        bjd=(dx/point_a.Ed+point_a.m_Rad_lo)*180./math.pi
        bwd=(dy/point_a.Ec+point_a.m_Rad_la)*180./math.pi
        return MyLatLng(bjd, bwd)

    @staticmethod
    def get_str(num):
        dec = int(num)
        min = int((num - dec) * 60)
        sec = int(((num - dec) * 60 - min) * 60)
        return "%03d%02d%02d\n" % (dec, min, sec)

    '''
	/**
	 * 获取AB连线与正北方向的角度
	 * @param A  A点的经纬度
	 * @param B  B点的经纬度
	 * @return  AB连线与正北方向的角度（0~360）
	 */
    '''
    @staticmethod
    def get_angle(point_a, point_b):
        dx = (point_b.m_Rad_lo-point_a.m_Rad_lo)*point_a.Ed
        dy = (point_b.m_Rad_la-point_a.m_Rad_la)*point_a.Ec
        angle = math.atan(math.fabs(dx/dy))*180./math.pi
        d_lo = point_b.m_Longitude-point_a.m_Longitude
        d_la = point_b.m_Latitude-point_a.m_Latitude
        if (d_lo > 0) and (d_la <= 0):
            angle = (90.-angle)+90
        elif (d_lo <= 0) and (d_la < 0):
            angle += 180.
        elif (d_lo < 0) and (d_la >= 0):
            angle = (90.-angle)+270
        return angle

    @staticmethod
    def get_radius(point_a, point_b):
        return math.radians(AngleUtil.get_angle(point_a, point_b))

    @staticmethod
    def get_vector(point_a, point_b):
        dx = point_b.m_Rad_la*point_b.Ec - point_a.m_Rad_la*point_a.Ec
        dy = (point_b.m_Rad_lo-point_a.m_Rad_lo)*point_a.Ed
        dz = (point_b.m_Rad_la-point_a.m_Rad_la)*point_a.Ec
        return dx, dy, dz

    @staticmethod
    def get_vector_radius(x_t, y_t):
        x = numpy.array(list(x_t))
        y = numpy.array(list(y_t))
        lx = numpy.sqrt(x.dot(x))
        ly = numpy.sqrt(y.dot(y))
        cos_angle = x.dot(y) / (lx * ly)
        return numpy.arccos(cos_angle)

    @staticmethod
    def get_3_points_radius(internal_point_1, internal_point_2, point):
        vector_1 = AngleUtil.get_vector(point, internal_point_1)
        vector_2 = AngleUtil.get_vector(point, internal_point_2)
        return AngleUtil.get_vector_radius(vector_1, vector_2)

if __name__ == '__main__':
    A = MyLatLng(113.249648, 23.401553)
    B = MyLatLng(113.246033, 23.403362)
    print AngleUtil.get_angle(A, B)

    A = MyLatLng(long_lat='232405N1131458E')
    B = MyLatLng(long_lat='232412N1131445E')
    print AngleUtil.get_angle(A, B)
    print AngleUtil.get_radius(A, B)
