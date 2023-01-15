# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 06:15:07 2022

This code simulates pk of some cups of coffee.
One "cup" contains something between 40 and 300 mg caffeine. I assume 120mg.
The dose is important because pk variables seems to be related to the dose.
 
The two main articles I got the pk data from are:
https://www.sciencedirect.com/science/article/abs/pii/S0378517301009589
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4898153/pdf/ictx-54-308.pdf


"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

#%%constants
ka=  0.033#0.033#abs constant min-1, central value from all the proposed values in article
kel= np.log(2)/450 #elim constant min-1, same as above.
Vd= 0.7*70 #distribution volume, same as above, L*Kg-1
D= 120#dose, mg
Vdepot= 0.2 #volume at depot site (L) (cup coffe 200mL)

t_frame= 24*60 #15 hours in minutes
t_span= np.arange(0,t_frame)

#to initialize curves
Ap= np.zeros(t_frame)
Ag= np.zeros(t_frame)

#%% plot me

fig= plt.figure('Simulation caffeine absorption',
                figsize=(14,9))


ax_plasma= fig.add_subplot(111)
#ax_plasma.set_yscale('log')
plt.subplots_adjust(bottom= 0.3)
ax_plasma.set_title('Caffeine concentration (plasma) after 1, 2 and 3 oral 120mg intake')

ax_plasma.set_xlabel('Time after the first cup (hours)')
ax_plasma.set_ylabel('Concentration in plasma, ug/mL')
ax_plasma.grid()
ax_plasma.set_xlim([0,t_frame/60])
ax_plasma.set_ylim([0,6])

tick_ref= np.arange(0,t_frame+60,60)/60
ax_plasma.set_xticks(tick_ref )
#ax_plasma.set_xticklabels([x+6 for x in range(len(tick_ref))])
l1, = ax_plasma.plot([],[], c= 'C1', label= 'first cup')
l2, = ax_plasma.plot([],[], c= 'C2', label= 'second cup')
l3, = ax_plasma.plot([],[], c= 'C3', label= 'third cup')

#create axes for sliders
ax_ka= plt.axes([0.20,0.16, 0.4, 0.02])
ax_kel= plt.axes([0.20,0.10, 0.4, 0.02])
ax_vd= plt.axes([0.20,0.04, 0.4, 0.02])
slide_ka= Slider(ax_ka, r'Absorption (K$_{a}$), min$^{-1}$', 0.015, 0.05, ka )
slide_kel= Slider(ax_kel, r'Elimination (K$_{10}$), min$^{-1}$', kel*0.55, kel*1.45, kel)
slide_vd= Slider(ax_vd, r'Vd mL Kg$^{-1}$', 0.55,0.85, Vd/70)

ax_plasma.legend()






#plt.show()
#%% Calculations. A is amounts. p is plasma, g is gastric or intestinal

def calculator(params):
    k_a, k_el, V_d= params
    Ap= np.zeros(t_frame)
    Ag= np.zeros(t_frame)
    
    cups_at= [1,180,360]
    
    curves= np.zeros(t_frame)
    
    for c in cups_at:
        
        Ag[c-1]= Ag[c-1]+D
        for t in range(c,t_frame): #18 hours in minutes
            deltaAg= Ag[t-1]*k_a
            deltaAp= -Ap[t-1]*k_el
            Ag[t]= Ag[t-1] - deltaAg
            Ap[t]= Ap[t-1] + deltaAp +deltaAg
    
        Cp= Ap/V_d 
        
        curves= np.vstack((curves,Cp)) #spare all the generated curves in one array
    
    l1.set_data(t_span/60, curves[1,:]) #/60 so time showed in hours.
    l2.set_data(t_span/60, curves[2,:])
    l3.set_data(t_span/60, curves[3,:])
    #plt.show()

#%% Plot initial curves
calculator([ka, kel, Vd])

#%% to make the sliders work...
    
def slider_update(val):
    ka= slide_ka.val
    kel= slide_kel.val
    Vd= slide_vd.val *70
    params=[ka, kel, Vd]
    
    calculator(params)
  
slide_ka.on_changed(slider_update)
slide_kel.on_changed(slider_update)
slide_vd.on_changed(slider_update)

plt.show()

