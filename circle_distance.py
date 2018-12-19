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


class Point:
  def __init__(self, long, lat, isstr=False, level=0):
    self.lr = 6378137.0
    self.sr = 6356752.3142
    if isstr:
      self.lat, self.long = parse_lat_long(long, lat)
    else:
      self.long = long
      self.lat = lat
    self.r = self.lr - self.lat/90 *(self.lr - self.sr) + level
    self.x = self.r * math.cos(math.radians(self.lat)) * math.cos(math.radians(self.long))
    self.y = self.r * math.cos(math.radians(self.lat)) * math.sin(math.radians(self.long))
    self.z = self.r * math.sin(math.radians(self.lat))


def angle(p1, p2):
  tmp1 = p1.x*p2.x + p1.y*p2.y + p1.z * p2.z
  p1l = math.sqrt(p1.x*p1.x + p1.y*p1.y + p1.z * p1.z)
  p2l = math.sqrt(p2.x*p2.x + p2.y*p2.y + p2.z * p2.z)
  return math.acos(tmp1/p1l/p2l)


def circle_distance(p1, p2):
  a1 = angle(p1,p2)
  return (p1.r + p2.r)*a1/2


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


if __name__ == "__main__":
#  print circle_distance(Point(116.0000, 36.79333), Point(115.6779, 36.66582)) #/ 1852
#  print circle_distance(Point("351122N1243344E", "", True), Point("351122N1243344E", "", True))
  fdp_vol = parseFDPVOL('FDP_VOLUMES_DEFINITION.ASF')
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
  draw_sec(fdp_vol, ["SH03E", "SH03W", "SH5E", "SH5W", "SH15", "SH01N", "SH01S", "SH20N", "SH20S"], ax1)
  #ax1.plot_surface(Y1, Z1, X1, rstride=1, cstride=1, cmap=cm.coolwarm, linewidth=0, antialiased=False)
  plt.show()