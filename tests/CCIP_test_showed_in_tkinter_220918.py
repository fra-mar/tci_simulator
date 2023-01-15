# -*- coding: utf-8 -*-
"""
Created on Sat Aug  6 05:13:41 2022

@author: Admin

Computer Controlled Infusion Pump simulator based on 
Shafer and Gregg J Pharmacokin Biopharm 1992;20:147-169

When Ce reaches Cet the Cp wobbles to a lot around, so in this code the solution
given in Apendix  1 is used. I.e. use the "simple analytical solution" in 
Bailey, Shafer IEEE transactions biological engineering 1991;38:322 to aim
for plasma concentration when Ce has reached the target.

To calculate expected plasma concentration at t + 2*delta with no infusion running
I used differential equations with scipy.integrate odeint function.

There is a slightly more complicated but easier to understand method by Jacobs:
IEEE transactions biomedical engineering 1990;37:107-109




This version adds buttons to control Cet

"""
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.widgets import Button
import tkinter as tk
from tkinter import ttk
import numpy as np
from scipy.integrate import odeint
from argparse import ArgumentParser

#%%load parameters
parser= ArgumentParser()
parser.add_argument( 'model', type=str)
parser.add_argument( 'age', type=float)
parser.add_argument( 'weight', type=float)
parser.add_argument( 'height', type=int)
parser.add_argument( 'gender', type=str)
args=parser.parse_args()

model= args.model
age= args.age
weight= args.weight
height= args.height
gender= args.gender

if model== 'Schnider, propofol':
    from schneider_params_calculator import schneider_params_calc
    params= schneider_params_calc(gender,age,weight,height)

if model== 'Minto, remifentanil':
    from minto_params_calculator import minto_params_calc
    params= minto_params_calc(gender,age,weight,height)
    
if model== 'Gepts, sufentanil':
    from sufenta_gepts_params_calculator import sufenta_params_calc
    params= sufenta_params_calc()

if model== 'Eleveld, propofol':
    from eleveld_propofol_params_calculator import eleveld_params_calc
    params= eleveld_params_calc(gender,age,weight,height)

#%%initial parameters
upd_time= 10 #the pump is updated every ten seconds
step= 0 #pump changes infusion rate in steps, upd_time apart.
d_time= 1 #calculations made for this seconds interval

params[6:]= [k/60 for k in params[6:]] #converts microrate_k to min^-1 to s^-1
model, drug_name, units, vd_1, vd_2, vd_3, k10, k12, k21, k13, k31, ke0= params #vol in L^-1
#Model is seen as a 4-compartment, considering effect compartment the 4th
#Being its vd 1/1e4th av central and thus its microrate constants k14, k41
vd_4= vd_1/1e4
k41= ke0 
k14= ke0/1e4

k1= k10+k12+k13+k14 #to simplify equations

cv= 0.25 #arbitrary variation coefficient to show a confidence interval for C4

#AMOUNTS of drug in each compartment
A1= np.zeros(1) 
A2= np.zeros(1)
A3= np.zeros(1)
A4= np.zeros(1)
#concentrations 
C1= np.zeros(1) 
C2= np.zeros(1)
C3= np.zeros(1)
C4= np.zeros(1) 
#time keeper
t_counter= np.zeros(1)
#infusion rate in AMOUNT* s^-1
I= 0.
I_log= np.zeros(1) #an I log
#initial Cet
Cet= 0.
newCet= 0.


#%% Calculating tpeak. This needs to be done just once before inf starts
a1, a2, a3, a4= 0, 0, 0, 0
j=1
e=[]
while True:
    if j<11 : #because it's a 10 seconds infusion
        delta_a1= a2*k21 + a3*k31 + a4*k41 - a1*k1 + 1 #for a unity infusion
    else:
        delta_a1= a2*k21 + a3*k31 + a4*k41 - a1*k1 
    
    delta_a2= a1*k12 - a2*k21 
    delta_a3= a1*k13 - a3*k31 
    delta_a4= a1*k14 - a4*k41 
    
    a1= a1 + delta_a1
    a2= a2 + delta_a2 
    a3= a3 + delta_a3 
    a4= a4 + delta_a4
    
    e.append(a4)
    j= j+1 
    if len(e) > 2:
        if e[-1] < e[-2]:
            e.pop() #remove last value to adapt length for future calculations
            e[0]=e[1]/1e3 #this prevents a division by zero later on
            break 
    if j==10:
        print(a1/vd_1)
        Cp_at_10_inf_unit= a1/vd_1 #variable useful to prevent wobbling of Cp
t_peak= j-2

#%% t_peak calculator for new infusion rate search algorithm
def j_peak_calc(i0, E, B4):
    global t_peak , added_amounts,j_peak1
    added_amounts= B4 + E*i0
    j_peak1= np.argmax(added_amounts) + 1 #to correct missmatch index-time
    return j_peak1

#%% New infusion rate(I) when Cet is changed
def newI(target):
    global e, b_e, j_p0, j_p1 , Aet
    Aet= target*vd_4 #calculates AMOUNT target
    #first amount in drug in effect site  at t+ t_peak if no drug was given
    b_e= [] #array for amount in compartment4 (effect site)
    b1= A1[-1]
    b2= A2[-1]
    b3= A3[-1]
    b4= A4[-1]
    
    for j in range(1,t_peak+1):
        delta_b1= b2*k21 + b3*k31 + b4*k41 - b1*k1
        delta_b2= b1*k12 - b2*k21 
        delta_b3= b1*k13 - b3*k31 
        delta_b4= b1*k14 - b4*k41 
        
        b1= b1 + delta_b1
        b2= b2 + delta_b2 
        b3= b3 + delta_b3 
        b4= b4 + delta_b4
        
        b_e.append(b4)
    #second, search for j_peak and I_updated
    j_p0= t_peak 
    j_p1= t_peak #dummy value to allow start while loop
    
    while True:
   
        I0= (Aet - b_e[j_p0-1]) / e[j_p0-1]          
        j_p1= j_peak_calc(I0, np.array(e), np.array(b_e))
        if I0< 0:
            I0= 0
        
        #print(f'j_p0: {j_p0} - j_p1: {j_p1} - i0: {I0:.4f}')
        
        if j_p0 == j_p1:
            break
        else:
            j_p0= j_p1
        
    return I0


#%% differential equations
def deriv(y, t, infRate):
    c1, c2, c3, c4 = y
    
    dc1dt= (infRate/vd_1) + c2*k21*vd_2/vd_1 + c3*k31*vd_3/vd_1 -c1*(k10+k12+k13)
    dc2dt= c1*k12*vd_1/vd_2 - c2*k21
    dc3dt= c1*k13*vd_1/vd_3 - c3*k31
    dc4dt= c1*k14/vd_4 - c4*k41
    
    return  dc1dt, dc2dt, dc3dt, dc4dt

#%% Integrate the pk equation over the time grid, t.

def future_C():
    #t_future: concentrations at the given inf rate in the future
    global t_future
    span= t_counter[-1] + 15*40 #to predict 15 seconds ahead
    t_future=np.linspace(t_counter[-1], span, 15*60)
    
    init_conditions_I0= C1[-1],C2[-1],C3[-1],C4[-1]#for I=0, used to calculate inf rate in SS
    
    
    ret_0= odeint(deriv, init_conditions_I0, t_future, args=(0,) )
    
    c1_int_0, c2_int_0, c3_int_0, c4_int_0 = ret_0.T
    
    return  c1_int_0

#%% Calculates Inf Rate when Cp is close to Ce, close to target

def I_from_Cp(target):
    r0= future_C()
    
    infRate= (Cet -r0[15])/Cp_at_10_inf_unit
   
    #print(infRate)
    return infRate

#%% Plot it

root=tk.Tk()
fig= Figure(figsize=(15,8))
figure_canvas= FigureCanvasTkAgg(fig, root)
NavigationToolbar2Tk(figure_canvas, root)

plt.subplots_adjust(bottom= 0.15)

fig.suptitle(f'{drug_name} ({model}).', fontsize= 20)

spec = gridspec.GridSpec(ncols=2, nrows=1,
                         wspace=0.2,
                         hspace=0.5, width_ratios=[3, 1])
ax_c= fig.add_subplot(spec[0]) #for concentrations
ax_a= fig.add_subplot(spec[1]) #for amounts
ax_c.set_xlim([0,800])
ax_a.set_xlim([0,820])
ax_c.set_ylim([0,20])
ax_a.set_ylim([0,0.5])
ax_c.grid()
ax_a.grid()
ax_c.set_xlabel('Seconds')
ax_c.set_ylabel(f'Concentrations in {units[0]}')
ax_a.set_xlabel('Seconds')
ax_a.set_ylabel(f'Infusion Rate in {units[1]}')

# control buttons, definitions and functions

ax_button_up= plt.axes([0.2, 0.02, 0.03, 0.05])
ax_button_down= plt.axes([0.25, 0.02, 0.03, 0.05])
ax_button_ok= plt.axes([0.3, 0.02, 0.03, 0.05])
ax_button_up.text (-2.5, 0.7, 'New Cet', 
                      fontsize= 14, color = 'darkgreen')
button_up= Button(ax_button_up, 'Up', color= 'bisque')
button_down= Button(ax_button_down, 'Down', color= 'bisque')
button_ok= Button(ax_button_ok, 'Ok', color= 'tomato')
def cet_up(val):
    global newCet 
    newCet= newCet + 0.2 
    print (newCet)
def cet_down(val):
    global newCet
    newCet= newCet - 0.2
    if newCet <0.:
        newCet= 0.
def set_new_cet(val):
    global newCet, Cet 
    Cet= newCet

button_up.on_clicked(cet_up)
button_down.on_clicked(cet_down)
button_ok.on_clicked(set_new_cet)



#init lines for amount
la,= ax_a.plot([],[], c='C4', label= 'Infusion Rate')

#init lines for concentration
lc_C4, = ax_c.plot([],[], c='C4', label= 'Effect', lw= 4)
lc_C1, = ax_c.plot([],[], c='C1', label= 'Central')
lc_C2, = ax_c.plot([],[], c='C2', label= 'Rapid peripheral', alpha= 0.4)
lc_C3, = ax_c.plot([],[], c='C3', label= 'Slow peripheral', alpha= 0.4)

#C4 confidence interval
lc_C4_u, =ax_c.plot([],[], c='C4', alpha=0.5) 
lc_C4_l, =ax_c.plot([],[], c='C4', alpha=0.5)



#init text
text_Cet = ax_c.text (0.12, 0.85, '', 
                      fontsize= 20,color = 'darkgreen',transform=ax_c.transAxes)
text_Ce = ax_c.text (0.32, 0.85, '', 
                      fontsize= 20,color = '#2f847c',transform=ax_c.transAxes)
text_Cp = ax_c.text (0.52, 0.85, '', 
                      fontsize= 20,color = '#2f847c',transform=ax_c.transAxes)
text_I = ax_a.text (0.1, 0.85, '', 
                      fontsize= 20,color = '#2f847c',transform=ax_a.transAxes)
text_dose= ax_a.text (0.09, 0.75, '', 
                      fontsize= 20,color = '#2f847c',transform=ax_a.transAxes)
text_time= ax_c.text(0.76, 0.65, '', 
                      fontsize= 50,color = '#2f847c',
                      alpha=0.3, transform=ax_c.transAxes)
ax_c.text(0.765, 0.75, 'min', fontsize=20, color= '#2f847c',
                      alpha=0.3, transform=ax_c.transAxes)
text_newCet= ax_button_up.text (-2.5,0, '', 
                      fontsize= 18, color = 'darkgreen')

#titles and legends
ax_c.legend()
ax_a.legend()
#ax_c.set_title('Concentrations')
ax_a.set_title('Infusion Rate')

figure_canvas.get_tk_widget().pack()

#%% Main loop
t= 0
while True:
    for tt in range(t, t+10):
        
        delta_A1= A2[-1]*k21 + A3[-1]*k31 + A4[-1]*k41 - A1[-1]*k1 + I
        delta_A2= A1[-1]*k12 - A2[-1]*k21 
        delta_A3= A1[-1]*k13 - A3[-1]*k31
        delta_A4= A1[-1]*k14 - A4[-1]*k41
        new_A1= A1[-1] +delta_A1
        new_A2= A2[-1] +delta_A2
        new_A3= A3[-1] +delta_A3
        new_A4= A4[-1] +delta_A4
        
        #update np.arrays
        A1= np.hstack((A1,new_A1))
        A2= np.hstack((A2,new_A2))
        A3= np.hstack((A3,new_A3))
        A4= np.hstack((A4,new_A4))
        C1= np.hstack((C1,new_A1/vd_1))
        C2= np.hstack((C2,new_A2/vd_2))
        C3= np.hstack((C3,new_A3/vd_3))
        C4= np.hstack((C4,new_A4/vd_4))
        
        I_log= np.hstack((I_log, I))
        
        t_counter= np.hstack((t_counter,tt))
        
        #plot this
        if t>500:
            ax_c.set_xlim([t_counter[-1]-500,t_counter[-1]+300])
            ax_a.set_xlim([t_counter[-1]-500,t_counter[-1]+300])
        
        la.set_data(t_counter, I_log)
    
        lc_C1.set_data(t_counter, C1)
        lc_C2.set_data(t_counter, C2)
        lc_C3.set_data(t_counter, C3)
        lc_C4.set_data(t_counter, C4)
        ax_c.collections.clear()
        ax_c.fill_between(t_counter, C4*(1+ 2*cv),C4*(1- 2*cv), 
                          color= 'C4', alpha= 0.1)
        ax_c.fill_between(t_counter, C4*(1+ cv),C4*(1- cv), 
                          color= 'C4', alpha= 0.2)
        
        
        text_Cet.set_text(f'Cet: {Cet:.1f}')
        text_Ce.set_text(f'Ce: {C4[-1]:.2f}')
        text_Cp.set_text(f'Cp: {C1[-1]:.2f}')
        text_I.set_text(f'I: {I:.2f}')
        text_dose.set_text(f'TotalDose: {np.sum(I_log):.1f}')
        text_time.set_text(f'{t_counter[-1]/60:.1f} ')
        text_newCet.set_text(f'{newCet:.1f}')

        plt.pause(0.2) #This decides the simulation speed
        
        

    
    #update infusion rate
    
    if C4[-1]> Cet*0.99 and C4[-1]< Cet*1.01:
        
        
        print('C4 in Cet range')
        I= I_from_Cp(Cet) 
        
    else:
        I= newI(Cet) 
    
    
    t= t+10
    ax_c.scatter(t, 0.2, marker='o', color= 'red', s=10, alpha= 0.5)
        
    
        



    



    

