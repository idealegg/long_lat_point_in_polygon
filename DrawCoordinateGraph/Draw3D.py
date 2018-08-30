import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(1,1,1, projection='3d')
theta = np.linspace(-4 * np.pi, 4 * np.pi, 500)
z = np.linspace(0,2,500)
r =z
x = r * np.sin(theta)
y = r * np.cos(theta)
ax.plot(x, y, z, label='curve')
ax.legend()
plt.show()


fig = plt.figure()
ax = fig.add_subplot(1,1,1, projection='3d')
xx = np.linspace(0, 5, 10)
yy = np.linspace(0, 5, 10)
zz1 = xx
zz2 = 2 * xx;
zz3 = 3 * xx
ax.scatter(xx, yy, zz1, c = 'red', marker='o')
ax.scatter(xx, yy, zz2, c = 'green', marker='^')
ax.scatter(xx, yy, zz3, c = 'black', marker='*')
ax.legend()
plt.show()

from matplotlib import cm
fig = plt.figure()
ax = fig.gca( projection='3d')
X = np.arange(-5,5,0.25)
Y = np.arange(-5,5,0.25)
X, Y = np.meshgrid(X, Y)
Z = X ** 2 + Y ** 2
ax.plot_surface(X, Y, Z, rstride=1,cstride =1, cmap =cm.coolwarm,\
               linewidth = 0,antialiased = False)
plt.show()


from matplotlib import cm
fig = plt.figure()
ax = fig.gca( projection='3d')
X = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0]
Y = [0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0]
X, Y = np.meshgrid(X, Y)
Z = [0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0]
ax.legend()
ax.plot_surface(X, Y, Z, rstride=1,cstride =1, cmap =cm.coolwarm,\
               linewidth = 0,antialiased = False)
plt.show()