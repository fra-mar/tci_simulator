#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 07:12:22 2022

@author: paco

This script simulates tricompartimental model for propofol according to
Schneider's model. See Anesthesiology 1998;88:1170

Plasma concentrations, not effect site. Fixed administration rate.

Regarding units: volumnes in L, dose in mg, therefore conc in microg/mL
"""
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import numpy as np
from schnider_params_calculator import lbm_calc, schnider_params_calc

weight= 75 #kg
height= 170 #cm
age= 85 #yr
gender= 'f'
lbm= lbm_calc(gender, weight, height)
f=weight*6/60 #administration rate weight* mg/Kg/h (/60 makes it /min)
#f=0   #activate this when simulating awakening
c1_init=0 #initial conc at central compartment (1)
c2_init=0 #initial conc at rapid_peripheral compartment (2)
c3_init=0 #initial conc at slow_peripheral compartment (3)
#c1_init, c2_init_,c3_init= 4,15,200
params= schnider_params_calc(age,
                              weight,
                              height,
                              lbm)
vd_1,vd_2,vd_3,k10,k12,k21,k13,k31= params


timespan= 2*60 #n hours, in minutes
t= np.linspace(0,timespan,100)
timesteps= timespan/1000
c1= np.zeros(t.shape) #concentration at every t (mg/L), central compartment
c2= np.zeros(t.shape) #concentration at every t (mg/L), RapidPeriph compartment
c3= np.zeros(t.shape) #concentration at every t (mg/L), SlowPeriph compartment

#%% how diferential equations interact, and initial conditions
def deriv(y, t):
    c1, c2, c3 = y
    
    dc1dt= (f/vd_1) + c2*k21*vd_2/vd_1 + c3*k31*vd_3/vd_1 -c1*(k10+k12+k13)
    dc2dt= c1*k12*vd_1/vd_2 - c2*k21
    dc3dt= c1*k13*vd_1/vd_3 - c3*k31
    
    return  dc1dt, dc2dt, dc3dt

y0 = c1_init, c2_init, c3_init #tuple with initial conditions

#%% Integrate the pk equation over the time grid, t.

#remeber, volumes in L and mass in mg, therefore conc microg/mL
ret = odeint(deriv, y0, t )
c1_integrated, c2_integrated, c3_integrated = ret.T

#%% Plot me

text_kwargs = dict(ha='right', va='center', fontsize=16)

fig= plt.figure('Schnider_propofol', figsize=(14,10))
ax= fig.add_subplot(111)
plt.subplots_adjust(bottom= 0.35)


l1, = ax.plot(t, c1_integrated, 
        color='C1', linewidth= 2, label= 'Central')
l2, =ax.plot(t, c2_integrated, 
        color='C2', ls=':',linewidth= 2, label= 'Rapid_peripheral')
l3, =ax.plot(t, c3_integrated, 
        color='C3', ls=':',linewidth= 1, label= 'Slow_peripheral')

ax.hlines(2.95,-12,timespan+2, lw=16, alpha=0.1, color= 'blue')
ax.text(-10,2.9,'$C_{50}$')
ax.set_xlim([-12,timespan+2])
ax.grid(alpha=0.3)
ax.set_ylim([0,4])
ax.legend()
ax.set_xlabel('Time in minutes')
ax.set_ylabel(r'Concentration in $\mu g\ ml^{-1}$')
ax.set_title('Schenider_propofol. PLASMA (not effectsite) concentration')

#Create axes for weight
ax_age= plt.axes([0.15,0.22, 0.5, 0.02])   #left, bottom, width,height
ax_weight= plt.axes([0.15,0.16, 0.5, 0.02])
ax_height= plt.axes([0.15,0.10, 0.5, 0.02])
ax_infRate= plt.axes([0.15,0.04, 0.5, 0.02])
ax_button_female= plt.axes([0.75, 0.16, 0.04, 0.05])
ax_button_male= plt.axes([0.75, 0.04, 0.04, 0.05])

#Create slider for age, weight, height, infusion rate
slide_age= Slider(ax_age, 'Age (yr)', 15.0, 100.0, 50.0, valstep=1.0)
slide_weight= Slider(ax_weight, 'Weight (Kg)', 30.0,110.0, weight, valstep=0.1 )
slide_height= Slider(ax_height, 'Height (cm)', 120,210, 160, valstep=1)
slide_infRate= Slider(ax_infRate, 'InfRate mg/Kg/t', 0.0, 15.0, f)
button_female= Button(ax_button_female, 'Female', color= 'yellow')
button_male= Button(ax_button_male, 'Male', color= 'orange')

#function that updates lines when sliders or buttons are changed
def updater(parameters, infRate):
    
    global f, vd_1,vd_2,vd_3,k10,k12,k21,k13,k31 
    f= infRate
    vd_1,vd_2,vd_3,k10,k12,k21,k13,k31= parameters
    ret = odeint(deriv, y0, t )
    c1_integrated, c2_integrated, c3_integrated = ret.T
    l1.set_ydata(c1_integrated)
    l2.set_ydata(c2_integrated)
    l3.set_ydata(c3_integrated)
    
#specific function for sliders
def slider_update(val):

    age= slide_age.val
    weight= slide_weight.val
    height= slide_height.val
    f= slide_infRate.val
    lbm= lbm_calc(gender, weight, height)
    params= schnider_params_calc(age,
                                  weight,
                                  height,
                                  lbm)
    updater(params, f)
    
#specific functions for buttons   
def b_male(val):
    global gender, weight, height, f
    gender= 'm'
    lbm= lbm_calc(gender, weight, height)
    params= schnider_params_calc(age,
                                  weight,
                                  height,
                                  lbm)
    updater(params, f)
    
def b_female(val):
    global gender, weight, height, f
    gender= 'f'
    lbm= lbm_calc(gender, weight, height)
    params= schneider_params_calc(age,
                                  weight,
                                  height,
                                  lbm)
    updater(params, f)

#call update function when a slider or button is changed/clicked
slide_age.on_changed(slider_update)
slide_weight.on_changed(slider_update)
slide_height.on_changed(slider_update)
slide_infRate.on_changed(slider_update)
button_male.on_clicked(b_male)
button_female.on_clicked(b_female)
    
plt.show()