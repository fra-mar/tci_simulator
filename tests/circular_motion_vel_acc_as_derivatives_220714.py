#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 18:53:03 2022

@author: paco
"""
import numpy as np
import matplotlib.pyplot as plt

r= 350


fig, ax= plt.subplots()
ax.set_aspect('equal')
ax.set_xticklabels([])
ax.set_yticklabels([])

a_range= np.linspace(0, 2*np.pi,360)
xx= r* np.cos(a_range)# points x and y as a function of sin, cos and r
yy= r* np.sin(a_range)

ax.scatter(xx,yy,s=1, c= 'b', alpha= 0.5)   #plots the circle

#calculate x and y component of v, as first derivative of a_range
vvx= -r* np.sin(a_range)
vvy= r* np.cos(a_range)

#calculate xy components of a, as second derivative of a_range
aax= -r* np.cos(a_range)
aay= -r* np.sin(a_range)

#plot just a few velocity and corresponding acceleration vectors

plt.scatter(0,0,s= 20,c='black') #pinpoints center

for i in range(0, len(a_range), 60):
    
    plt.scatter(xx[i], yy[i], c= 'b', s= 20) #pinpoints the analized point
    
    ax.quiver(xx[i],yy[i], vvx[i], vvy[i], #velocity vectors
              units= 'x', scale= 2, color='g')
    
    ax.quiver(xx[i],yy[i], aax[i], aay[i],   #acceleration vectors
              units= 'x', scale= 2, color= 'r')

fig.suptitle('Velocity (green) and acceleration (red) vectors as 1st and 2nd derivatives')
plt.show()
