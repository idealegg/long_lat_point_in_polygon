import math

class Point:
  def __init__(self, long, lat):
    self.lr = 6378137.0
    self.sr = 6356752.3142
    self.long = long
    self.lat = lat
    self.r = self.lr - self.lat/90 *(self.lr - self.sr)
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


if __name__ == "__main__":
  circle_distance(Point(116.0000, 36.79333), Point(115.6779, 36.66582)) / 1852