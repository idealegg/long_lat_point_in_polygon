import math
import re
import pprint
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm


colors = (
  ('b', 'blue'),
  ('g', 'green'),
  ('r', 'red'),
  ('c', 'cyan'),
  ('m', 'magenta'),
  ('y', 'yellow'),
  ('k', 'black'),
  ('w', 'white'))

def parse_lat_long(long, lat):
  '''350000N1240000E'''
  t_long = 0
  t_lat = 0;
  p1 = re.compile("(\d{2,3})(\d{2})((\d{2})?)([NSEW])")
  for s in [long, lat]:
    ress = re.findall(p1, s)
    if len(ress) in [1, 2]:
      for res in ress:
        tmp = int(res[0], 10) + int(res[1], 10)/60.0 +int(res[3] or "0", 10)/3600.0
        if res[4] == 'N':
          t_lat = tmp
        elif res[4] == 'S':
          t_lat = -tmp
        elif res[4] == 'E':
          t_long = tmp
        elif res[4] == 'W':
          t_long = -tmp
  return t_lat, t_long

def angle(p1, p2):
  tmp1 = p1.x*p2.x + p1.y*p2.y + p1.z * p2.z
  p1l = math.sqrt(p1.x*p1.x + p1.y*p1.y + p1.z * p1.z)
  p2l = math.sqrt(p2.x*p2.x + p2.y*p2.y + p2.z * p2.z)
  return math.acos(tmp1/p1l/p2l)


def circle_distance(p1, p2):
  a1 = angle(p1,p2)
  return (p1.r + p2.r)*a1/2


class Point:
  def __init__(self, long, lat, isstr=False, level=0):
    self.lr = 6378137.0
    self.sr = 6356752.3142
    if isstr:
      self.lat, self.long = parse_lat_long(long, lat)
    else:
      self.long = long
      self.lat = lat
    self.level = level
    self.r = self.lr - self.lat/90 *(self.lr - self.sr) + level
    self.x = self.r * math.cos(math.radians(self.lat)) * math.cos(math.radians(self.long))
    self.y = self.r * math.cos(math.radians(self.lat)) * math.sin(math.radians(self.long))
    self.z = self.r * math.sin(math.radians(self.lat))

  def get2Dxy(self, centre):
    # level should be 0
    p1 = Point(self.long, centre.lat)
    p2 = Point(centre.long, self.lat)
    x = circle_distance(self, p1)
    y = circle_distance(self, p2)
    if self.lat < centre.lat:
      x = -x
    if self.long < centre.long:
      y = -y
    return x, y


def parseheight(height):
  res = re.match("S(\d{4})", height)
  if res:
    return int(res.group(1), 10)*10.0
  res = re.match("F(\d{3})", height)
  if res:
    return int(res.group(1), 10)*30.48

def parseFDPVOL(file):
  fd = open(file)
  fdp_vol = {'POINTS': {}, 'ARCS': {}, 'LAYER': {}, 'VOLUME': {}, 'SECTOR': {},
             'MIL_AREA': {}, 'EUROCAT_T_AREA': {}, 'NON_SURVEILLANCE_TOWER': {}, 'FIR': {}}
  cur_title = ""
  cur_vol = ""
  cur_sec = ""
  cur_fir = ""
  last_layer = 0
  for line in fd:
    line = line.strip()
    comment = line.find("--")
    if comment != -1:
      line = line[:comment]
    if line:
      res = re.match("/(\w+)/", line)
      if res:
        cur_title = res.group(1)
      elif cur_title == "POINTS":
        res = re.search("^(\w+)\s*\|\s*(\w+)", line)
        if res:
          fdp_vol['POINTS'][res.group(1)] =  res.group(2)
      elif cur_title == "ARCS":
        res = re.search("^(\w+)\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*(\w+)", line)
        if res:
          fdp_vol['ARCS'][res.group(1)] = {}
          fdp_vol['ARCS'][res.group(1)]['start'] = res.group(2)
          fdp_vol['ARCS'][res.group(1)]['end'] = res.group(3)
          fdp_vol['ARCS'][res.group(1)]['centre'] = res.group(4)
          fdp_vol['ARCS'][res.group(1)]['precision'] = res.group(5)
      elif cur_title == "LAYER":
        res = re.search("^(\w+)\s*\|\s*(\w+)", line)
        if res:
          fdp_vol['LAYER'][res.group(1)] = {}
          fdp_vol['LAYER'][res.group(1)]['layer'] = res.group(2)
          fdp_vol['LAYER'][res.group(1)]['max'] = parseheight(res.group(2))
          fdp_vol['LAYER'][res.group(1)]['min'] = last_layer
          last_layer = fdp_vol['LAYER'][res.group(1)]['max']
      elif cur_title == "VOLUME":
        res = re.search("^(\w+)\s*\|\s*(\w+)\s*\|\s*([\w\s]+)", line)
        if res:
          cur_vol = res.group(1)
          fdp_vol['VOLUME'][cur_vol] = {}
          fdp_vol['VOLUME'][cur_vol]['layer'] = res.group(2).lstrip('0')
          fdp_vol['VOLUME'][cur_vol]['points'] = res.group(3)
          fdp_vol['VOLUME'][cur_vol]['point_list'] = re.findall("\w+", fdp_vol['VOLUME'][cur_vol]['points'])
        else:
          res = re.search("^\s*\|\s*\|\s*([\w\s]+)", line)
          if res:
            fdp_vol['VOLUME'][cur_vol]['points'] = ' '.join([fdp_vol['VOLUME'][cur_vol]['points'], res.group(1)])
            fdp_vol['VOLUME'][cur_vol]['point_list'] = re.findall("\w+", fdp_vol['VOLUME'][cur_vol]['points'])
      elif cur_title == "SECTOR":
        line = line.replace("+", ' ')
        res = re.search("^(\w+)\s*\|\s*(\w+)\s*\|\s*([\w\s]+)", line)
        if res:
          cur_sec = res.group(1)
          fdp_vol['SECTOR'][cur_sec] = {}
          fdp_vol['SECTOR'][cur_sec]['precision'] = res.group(2)
          fdp_vol['SECTOR'][cur_sec]['vols'] = res.group(3)
          fdp_vol['SECTOR'][cur_sec]['vol_list'] = re.findall("\w+", fdp_vol['SECTOR'][cur_sec]['vols'])
        else:
          res = re.search("^\s*\|\s*\|\s*([\w\s]+)", line)
          fdp_vol['SECTOR'][cur_sec]['vols'] = ' '.join([fdp_vol['SECTOR'][cur_sec]['vols'], res.group(1)])
          fdp_vol['SECTOR'][cur_sec]['vol_list'] = re.findall("\w+", fdp_vol['SECTOR'][cur_sec]['vols'])
      elif cur_title in ('MIL_AREA', 'EUROCAT_T_AREA', 'NON_SURVEILLANCE_TOWER', 'FIR'):
        line = line.replace("+", ' ')
        res = re.search("^(\w+)\s*\|\s*([\w\s]+)", line)
        if res:
          cur_fir = res.group(1)
          fdp_vol[cur_title][cur_fir] = {}
          fdp_vol[cur_title][cur_fir]['vols'] = res.group(2)
          fdp_vol[cur_title][cur_fir]['vol_list'] = re.findall("\w+", fdp_vol[cur_title][cur_fir]['vols'])
        else:
          res = re.search("^\s*\|\s*([\w\s]+)", line)
          fdp_vol[cur_title][cur_fir]['vols'] = ' '.join([fdp_vol[cur_title][cur_fir]['vols'], res.group(1)])
          fdp_vol[cur_title][cur_fir]['vol_list'] = re.findall("\w+", fdp_vol[cur_title][cur_fir]['vols'])
  fd.close()
  return fdp_vol


def parseCHARPOINT(file):
  fd = open(file)
  char_point = {'DEFINITIONS': {}}
  cur_title = ""
  for line in fd:
    line = line.strip()
    comment = line.find("--")
    if comment != -1:
      line = line[:comment]
    if line:
      res = re.match("/(\w+)/", line)
      if res:
        cur_title = res.group(1)
      elif cur_title == "DEFINITIONS":
        res = re.search(
"^(\w+)\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*([\w\s]*)\s*\|\s*(\w+)\s*\|\s*(\w+)"
          , line)
        if res:
          char_point['DEFINITIONS'][res.group(1)] = {}
          char_point['DEFINITIONS'][res.group(1)]['Lat_Long'] = res.group(2)
          char_point['DEFINITIONS'][res.group(1)]['Type'] = res.group(3)
          char_point['DEFINITIONS'][res.group(1)]['Relevant_fix'] = res.group(4)
          char_point['DEFINITIONS'][res.group(1)]['Airport_Id'] = res.group(5)
          char_point['DEFINITIONS'][res.group(1)]['Pilot_display'] = res.group(6)
          char_point['DEFINITIONS'][res.group(1)]['DTI'] = res.group(7)
  fd.close()
  return char_point


def getlevel(layer, fdp_vol):
  layer1 = []
  res = re.match("(\d+)-(\d+)", layer)
  if res:
    layer1.append(res.group(1))
    layer1.append(res.group(2))
  else:
    layer1.append(layer)
    layer1.append(layer)
  #print "layer: %s\n" % layer
  return fdp_vol['LAYER'][layer1[0]]['min'], fdp_vol['LAYER'][layer1[1]]['max']


def getXYZ(fdp_vol, vol_list):
  X = []
  Y = []
  Z = []
  X1 = []
  Y1 = []
  Z1 = []
  for vol in vol_list:
    for point in fdp_vol['VOLUME'][vol]['point_list']:
      level = getlevel(fdp_vol['VOLUME'][vol]['layer'], fdp_vol)
      p = Point(fdp_vol['POINTS'][point], "", True, level[0])
      X.append(p.x)
      Y.append(p.y)
      Z.append(p.z)
      p = Point(fdp_vol['POINTS'][point], "", True, level[1])
      X1.append(p.x)
      Y1.append(p.y)
      Z1.append(p.z)
  return X, Y, Z, X1, Y1, Z1


def draw_vol(fdp_vol, vol, color, ax1):
  X, Y, Z, X1, Y1, Z1 = getXYZ(fdp_vol, [vol])
  ax1.plot_trisurf(X, Y, Z, linewidth=0.2, antialiased=True, color=color)
  ax1.plot_trisurf(X1, Y1, Z1, linewidth=0.2, antialiased=True, color=color)


def draw_sec(fdp_vol, secs, ax1):
  global colors
  i = 0
  for sec in secs:
    for vol in fdp_vol['SECTOR'][sec]['vol_list']:
      draw_vol(fdp_vol, vol, colors[i % len(colors)][0], ax1)
    i = i + 1


def draw_fir(fdp_vol, firs, ax1):
  global colors
  i = 0
  for fir in firs:
    for vol in fdp_vol['FIR'][fir]['vol_list']:
      draw_vol(fdp_vol, vol, colors[i % len(colors)][0], ax1)
    i = i + 1


def draw_route(char_point, route, ax1, level):
  X = []
  Y = []
  Z = []
  for point in route:
    if type(point) == type(()):
      if len(point) == 2:
        p = Point(point[1], point[0], False, level)
      else:
        p = Point(point[1], point[0], False, 0)
      name = "(%f, %f)"%(point[0], point[1])
    else:
      p = Point(char_point['DEFINITIONS'][point]['Lat_Long'], "", True, level)
      name = point
    X.append(p.x)
    Y.append(p.y)
    Z.append(p.z)
    ax1.text(p.x, p.y, p.z, name, color="b")
  #ax1.plot(X, Y, Z, linewidth=10)
  ax1.plot(X, Y, Z, 'ro')


def is_point_in_poly(p, poly):
  px, py = p
  flag = False
  l = len(poly)
  j = l - 1
  for i in range(l):
    sx, sy = poly[i]
    tx, ty = poly[j]
    # p cross vertex of poly
    if ((sx == px) and (sy == py)) or ((tx == px) and (ty == py)):
      return True
    # judge if the endpoints of segment are the sides of the radial
    if ((sy < py) and (ty >= py)) or ((sy >= py) and (ty < py)):
      x = sx + (py - sy) * (tx - sx) / (ty - sy)
      # p in the border of poly
      if x == px:
        return True
      # the radial cross the border of poly
      if x > px:
        flag = not flag
    j = i
    i += 1
  return flag


def is_point_in_vol(fdp_vol, p, vol, centre, plevel = 0):
  poly = []
  level = getlevel(fdp_vol['VOLUME'][vol]['layer'], fdp_vol)
  if plevel > level[1] or plevel < level[0]:
    return False
  for point in fdp_vol['VOLUME'][vol]['point_list'][:-1]:
    p1 = Point(fdp_vol['POINTS'][point], "", True)
    poly.append(p1.get2Dxy(centre))
  return is_point_in_poly(p.get2Dxy(centre), poly)


def is_point_in_fir(fdp_vol, p, fir, centre, plevel=0):
  for vol in fdp_vol['FIR'][fir]['vol_list']:
    if is_point_in_vol(fdp_vol, p, vol, centre, plevel):
      return True
  return False


if __name__ == "__main__":
  ps =[ (031.74, 0118.87, 129.54),
  (031.75, 0118.87, 228.6),
  (031.75, 0118.88, 312.42),
  (031.75, 0118.88, 403.86),
  (031.75, 0118.88, 411.48),
  (031.75, 0118.89, 449.58),
  (031.76, 0118.89, 518.16),
  (031.76, 0118.90, 548.64),
  (031.76, 0118.90, 571.5),
  (031.76, 0118.90, 594.36),
  (031.76, 0118.91, 678.18),
  (031.77, 0118.91, 754.38),
  (031.77, 0118.92, 822.96),
  (031.77, 0118.92, 883.92),
  (031.77, 0118.93, 990.6),
  (031.78, 0118.93, 1043.94),
  (031.78, 0118.94, 1104.9),
  (031.78, 0118.94, 1158.24),
  (031.79, 0118.95, 1272.54),
  (031.79, 0118.95, 1341.12),
  (031.80, 0118.95, 1402.08),
  (031.80, 0118.96, 1539.24),
  (031.81, 0118.96, 1623.06),
  (031.81, 0118.95, 1691.64),
  (031.82, 0118.95, 1760.22),
  (031.82, 0118.95, 1760.22),
  (031.82, 0118.95, 1897.38),
  (031.82, 0118.95, 1897.38),
  (031.83, 0118.95, 1973.58),
  (031.83, 0118.94, 2042.16),
  (031.84, 0118.94, 2171.7),
  (031.84, 0118.93, 2255.52),
  (031.84, 0118.93, 2324.1),
  (031.85, 0118.93, 2385.06),
  (031.85, 0118.92, 2506.98),
  (031.86, 0118.92, 2590.8),
  (031.86, 0118.92, 2651.76),
  (031.87, 0118.91, 2712.72),
  (031.87, 0118.91, 2804.16),
  (031.87, 0118.90, 2865.12),
  (031.88, 0118.90, 2926.08),
  (031.88, 0118.90, 2956.56),
  (031.89, 0118.89, 3017.52),
  (031.89, 0118.89, 3048),
  (031.90, 0118.88, 3078.48),
  (031.90, 0118.88, 3108.96),
  (031.91, 0118.87, 3200.4),
  (031.98, 0118.73, 4785.36),
  (031.98, 0118.72, 4876.8),
  (031.98, 0118.71, 4968.24),
  (031.98, 0118.71, 5090.16),
  (031.98, 0118.70, 5204.46),
  (031.98, 0118.69, 5273.04),
  (031.98, 0118.68, 5364.48),
  (031.98, 0118.68, 5440.68),
  (031.98, 0118.67, 5509.26),
  (031.98, 0118.66, 5562.6),
  (031.98, 0118.66, 5646.42),
  (031.98, 0118.65, 5707.38),
  (031.98, 0118.64, 5768.34),
  (031.98, 0118.63, 5821.68),
  (031.98, 0118.63, 5882.64),
  (031.98, 0118.53, 5996.94),
  (031.98, 0118.49, 6004.56)]

  #  print circle_distance(Point(116.0000, 36.79333), Point(115.6779, 36.66582)) #/ 1852
#  print circle_distance(Point("351122N1243344E", "", True), Point("351122N1243344E", "", True))
  fdp_vol = parseFDPVOL('FDP_VOLUMES_DEFINITION.ASF')
  char_point = parseCHARPOINT('CHARACTERISTIC_POINTS.ASF')
  centre = Point('311200N1212000E', '', True)
  for p in ps:
    print circle_distance(Point(p[1], p[0]), Point(char_point['DEFINITIONS']['ZSNJ']['Lat_Long'], "", True, 0))   / 1852
    print is_point_in_fir(fdp_vol, Point(p[1], p[0]), 'NJAP', centre)
  print circle_distance(Point(char_point['DEFINITIONS']['SUNBO']['Lat_Long'], "", True, 0), Point(char_point['DEFINITIONS']['ZSNJ']['Lat_Long'], "", True, 0)) / 1852
  print is_point_in_fir(fdp_vol, Point(char_point['DEFINITIONS']['SUNBO']['Lat_Long'], "", True, 0), 'NJAP', centre)
else:
  fdp_vol = parseFDPVOL('FDP_VOLUMES_DEFINITION.ASF')
  char_point = parseCHARPOINT('CHARACTERISTIC_POINTS.ASF')
  #pprint.pprint(fdp_vol)
  fig = plt.figure()
  ax1 = fig.add_subplot(1,1,1, projection='3d')
  #ax2 = fig.add_subplot(2, 1, 2, projection='3d')
  #ax = fig.gca(projection='3d')
  #X, Y, Z, X1, Y1, Z1 = getXYZ(fdp_vol, ['S03C01'])
#  X = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0]
#  Y = [0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0]
  #X, Y = np.meshgrid(X, Y)
#  Z = [0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0]
  #ax.set_title("Polys")
  #ax.set_xlabel('y')
  #ax.set_ylabel('z')
  #ax.set_zlabel('x')
  #ax.legend("haha")
  #ax.plot_surface(Y, Z, X, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)
  #ax.plot(X, Y, Z)
  #ax.contour(X,Y,Z, zdir = 'z')
  #ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)
  #ax1.plot_trisurf(X, Y, Z, linewidth=0.2, antialiased=True, color="g")
  #ax1.plot_trisurf(X1, Y1, Z1, linewidth=0.2, antialiased=True, color="g")
  #X, Y, Z, X1, Y1, Z1 = getXYZ(fdp_vol, ['TM1A01'])
  #ax1.plot_trisurf(X, Y, Z, linewidth=0.2, antialiased=True, color="r")
  #ax1.plot_trisurf(X1, Y1, Z1, linewidth=0.2, antialiased=True, color="r")
  #X1, Y1, Z1 = getXYZ('TM1A01', fdp_vol)
  #draw_sec(fdp_vol, ["SH03E", "SH03W", "SH5E", "SH5W", "SH15", "SH01N", "SH01S", "SH20N", "SH20S"], ax1)
  #draw_sec(fdp_vol, ["SH14L", "HFAC01", "HFAC04"], ax1)
  draw_fir(fdp_vol, ['NJAP'], ax1)
  draw_route(char_point, ['ZSNJ',
                          (031.74, 0118.87, 129.54),
                          (031.75, 0118.87, 228.6),
                          (031.75, 0118.88, 312.42),
                          (031.75, 0118.88, 403.86),
                          (031.75, 0118.88, 411.48),
                          (031.75, 0118.89, 449.58),
                          (031.76, 0118.89, 518.16),
                          (031.76, 0118.90, 548.64),
                          (031.76, 0118.90, 571.5),
                          (031.76, 0118.90, 594.36),
                          (031.76, 0118.91, 678.18),
                          (031.77, 0118.91, 754.38),
                          (031.77, 0118.92, 822.96),
                          (031.77, 0118.92, 883.92),
                          (031.77, 0118.93, 990.6),
                          (031.78, 0118.93, 1043.94),
                          (031.78, 0118.94, 1104.9),
                          (031.78, 0118.94, 1158.24),
                          (031.79, 0118.95, 1272.54),
                          (031.79, 0118.95, 1341.12),
                          (031.80, 0118.95, 1402.08),
                          (031.80, 0118.96, 1539.24),
                          (031.81, 0118.96, 1623.06),
                          (031.81, 0118.95, 1691.64),
                          (031.82, 0118.95, 1760.22),
                          (031.82, 0118.95, 1760.22),
                          (031.82, 0118.95, 1897.38),
                          (031.82, 0118.95, 1897.38),
                          (031.83, 0118.95, 1973.58),
                          (031.83, 0118.94, 2042.16),
                          (031.84, 0118.94, 2171.7),
                          (031.84, 0118.93, 2255.52),
                          (031.84, 0118.93, 2324.1),
                          (031.85, 0118.93, 2385.06),
                          (031.85, 0118.92, 2506.98),
                          (031.86, 0118.92, 2590.8),
                          (031.86, 0118.92, 2651.76),
                          (031.87, 0118.91, 2712.72),
                          (031.87, 0118.91, 2804.16),
                          (031.87, 0118.90, 2865.12),
                          (031.88, 0118.90, 2926.08),
                          (031.88, 0118.90, 2956.56),
                          (031.89, 0118.89, 3017.52),
                          (031.89, 0118.89, 3048),
                          (031.90, 0118.88, 3078.48),
                          (031.90, 0118.88, 3108.96),
                          (031.91, 0118.87, 3200.4),
                          (031.98, 0118.73, 4785.36),
                          (031.98, 0118.72, 4876.8),
                          (031.98, 0118.71, 4968.24),
                          (031.98, 0118.71, 5090.16),
                          (031.98, 0118.70, 5204.46),
                          (031.98, 0118.69, 5273.04),
                          (031.98, 0118.68, 5364.48),
                          (031.98, 0118.68, 5440.68),
                          (031.98, 0118.67, 5509.26),
                          (031.98, 0118.66, 5562.6),
                          (031.98, 0118.66, 5646.42),
                          (031.98, 0118.65, 5707.38),
                          (031.98, 0118.64, 5768.34),
                          (031.98, 0118.63, 5821.68),
                          (031.98, 0118.63, 5882.64),
                          (031.98, 0118.53, 5996.94),
                          (031.98, 0118.49, 6004.56),


                          'SUNBO', 'HFE', 'MAGLI', 'PEDNU', 'P343', 'BIPIM', 'FYG', 'ZHO'], ax1, 0)
  #draw_route(char_point, ['RKSI', 'PONIK', 'SADLI', 'LAMEN', 'AKARA', 'DUMET', 'IPRAG',
  #                        'PUD', 'JTN', 'OLGAP', 'NXD', 'KAKIS', 'OBGIV', 'TOL', 'ELNEX',
  #                        'SHR', 'P215', 'XUVGI', 'NF', 'P120', 'SAGON', 'PLT', 'MABAG'], ax1, 10393)
  #ax1.plot_surface(Y1, Z1, X1, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)
  plt.show()