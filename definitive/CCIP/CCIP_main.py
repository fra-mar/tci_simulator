# -*- coding: utf-8 -*-
"""
Created on Sat Aug  6 05:13:41 2022


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



"""
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.widgets import Button
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
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

#Activate for test / debugging
'''
weight= 75 #kg
height= 170 #cm
age= 35 #yr
gender= 'm'
'''
if gender== 'm':
    g_string= 'Male'
if gender== 'f':
    g_string= 'Female'


params[7:]= [k/60 for k in params[7:]] #converts microrate_k to min^-1 to s^-1
drug_name, model, units, ec50= params[:4]
print(drug_name)

vd_1, vd_2, vd_3, k10, k12, k21, k13, k31, ke0= params[4:] #vol in L^-1
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

paused= True #so the simulation doesn't run at once.
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
        #print(a1/vd_1)
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
        if I0< 0.:
            I0= 0.
        
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
   
    if infRate< 0.0:
        infRate= 0.
    return infRate

#%% Convert units to show nice infusion rates:
def I_weight_time(I):
    if drug_name== 'Propofol':
        return (I/weight)*3600
    elif drug_name== 'Sufentanil':
        return(I/weight)* 60
    elif drug_name== 'Remifentanil':
        return (I/weight)* 60
    else:
        print ('unknown drug')
        return I
        


#%%Plot the curves
fig= plt.Figure(figsize=(13,4), facecolor= '#f9cb9c')

spec = gridspec.GridSpec(ncols=2, nrows=1,
                         wspace=0.2,
                         hspace=0.2, width_ratios=[3, 1])

ax_c= fig.add_subplot(spec[0]) #for concentrations
ax_a= fig.add_subplot(spec[1]) #for amounts
ax_c.set_xlim([0,800])
ax_a.set_xlim([0,820])
ax_c.set_ylim([0,ec50*3])
ax_a.set_ylim([0,0.5])
ax_c.grid(alpha= 0.5)
ax_a.grid(alpha= 0.5)
ax_c.set_xlabel('Seconds')
ax_c.set_ylabel(f'Concentrations in {units[0]}')
ax_a.set_xlabel('Seconds')

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
fs= 18
text_Cet = ax_c.text (0.02, 0.91, '', 
                      fontsize= fs,color = 'darkgreen',transform=ax_c.transAxes)
text_Ce = ax_c.text (0.20, 0.91, '', 
                      fontsize= fs,color = '#2f847c',transform=ax_c.transAxes)
text_Cp = ax_c.text (0.38, 0.91, '', 
                      fontsize= fs,color = '#2f847c',transform=ax_c.transAxes)
text_I = ax_a.text (0.1, 0.85, '', 
                      fontsize= fs,color = '#2f847c',transform=ax_a.transAxes)
text_dose= ax_a.text (0.09, 0.75, '', 
                      fontsize= fs*0.7,color = '#2f847c',transform=ax_a.transAxes)
text_time= ax_c.text(0.82, 0.01, '', 
                      fontsize= fs*1.8 ,color = '#2f847c',
                      alpha=0.3, transform=ax_c.transAxes)
ax_c.text(0.76, 0.01, 'min', fontsize=fs*0.8, color= '#2f847c',
                      alpha=0.3, transform=ax_c.transAxes)
ax_c.text(0.0, 1.03, f'{drug_name}', fontsize=fs*1.8, color= '#2f847c',
                      alpha=0.8, transform=ax_c.transAxes)
ax_c.text(0.45, 1.03, f'{model}. {g_string}, {age:.0f}y, {weight}Kg, {height}cm', 
                      fontsize=fs*0.8, color= '#2f847c',
                      alpha=0.5, transform=ax_c.transAxes)
#titles and legends
ax_c.legend()

ax_a.set_title(f'Infusion Rate in {units[1]}')

#%% Main loop
t= 0



def gen(): #generates a number of frames if a condition is fullfilled
    global t
    frame = 0
    while True:
        frame += 1
        yield frame
       
def update(frame):
    
    
    global A1, A2, A3, A4, C1, C2, C3, C4
    global I, I_log, t, t_counter, newCet
    
    
    
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
    
    t_counter= np.hstack((t_counter,t))
    
    #plot this
    if t>600:
        ax_c.set_xlim([t_counter[-1]-600,t_counter[-1]+200])
        ax_a.set_xlim([t_counter[-1]-600,t_counter[-1]+200])
    
    la.set_data(t_counter, I_log)

    lc_C1.set_data(t_counter, C1)
    lc_C2.set_data(t_counter, C2)
    lc_C3.set_data(t_counter, C3)
    lc_C4.set_data(t_counter, C4)
    
    ax_c.collections.clear()
    
    
    fb1= ax_c.fill_between(t_counter, C4*(1+ 2*cv),C4*(1- 2*cv), 
                      color= 'C4', alpha= 0.1)
    
    fb2= ax_c.fill_between(t_counter, C4*(1+ cv),C4*(1- cv), 
                      color= 'C4', alpha= 0.2)
    
    text_Cet.set_text(f'Cet: {Cet:.1f}')
    text_Ce.set_text(f'Ce: {C4[-1]:.2f}')
    text_Cp.set_text(f'Cp: {C1[-1]:.2f}')
    text_I.set_text(f'IRate: {I_weight_time(I):.2f}')
    text_dose.set_text(f'TotalDose: {np.sum(I_log):.1f}')
    text_time.set_text(f'{t_counter[-1]/60:.1f} ')
    newCet_label['text']= f'{newCet:.2f}'
    
    #update infusion rate
    if t%10 == 0:
        if C4[-1]> Cet*0.99 and C4[-1]< Cet*1.01:
            
            I= I_from_Cp(Cet) 
            
        else:
            I= newI(Cet) 
    
    
    t= t+1
    
    return (lc_C1, lc_C2, lc_C3, lc_C4, la, fb1, fb2, text_Cet, 
            text_Ce, text_Cp, text_I, text_dose, text_time,)
 


#%%Create tkinter root window

root= tk.Tk()
#root.geometry('1800x1000')
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()


root.title(f'TCI simulator. {drug_name}, {model} model')

root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=7)

root.configure(bg= '#b0ebf4')

input_frame= ttk.Frame(root, 
                       borderwidth= 5, 
                       relief= 'raised', 
                       padding= 5,
                       height= 1600)
input_frame.grid(column=0, row=0)

show_frame= ttk.Frame(root, 
                       borderwidth= 5, 
                       relief= 'raised', 
                       padding= 5,
                       height= 1600)
show_frame.grid(column=1, row=0)

#%% Make a button in input_frame

def cet_up():
    global newCet 
    newCet= newCet + 0.1
    
def cet_down():
    global newCet
    newCet= newCet - 0.1
    if newCet <0.:
        newCet= 0.
def cet_set():
    global newCet, Cet 
    Cet= newCet
    
def paus_res():
    global paused
    if paused== False:
        ani.pause()
    if paused== True:
        ani.resume()
    paused= not paused

def exit_b():
    arr_to_save= np.hstack((t_counter.reshape(-1,1), 
                            C1.reshape(-1,1), 
                            C2.reshape(-1,1), 
                            C3.reshape(-1,1), 
                            C4.reshape(-1,1), 
                            I_log.reshape(-1,1)))
    
    np.savetxt('pkData.csv', arr_to_save, delimiter=',',
               header='Seconds,C1,C2,C3,C4,I')
    root.destroy()
    
up_button= ttk.Button(input_frame, text= 'UP', command= cet_up).grid(column= 0, 
                                                    row=0,
                                                    padx=5, pady=5)

down_button= ttk.Button(input_frame, text= 'DOWN', command= cet_down).grid(column= 0, 
                                                    row=3,
                                                    padx=5, pady=5)
set_button= ttk.Button(input_frame, text= 'SET', command= cet_set).grid(column= 0, 
                                                    row=4,
                                                    padx=5, pady=10)

pause_button= ttk.Button(input_frame, text= 'Paus/Resume', command= paus_res).grid(column= 0, 
                                                    row=7,
                                                    padx=5, pady=10)

    

exit_button= ttk.Button(input_frame, text= 'EXIT', 
                        command= exit_b).grid(column= 0, 
                                                    row=5,
                                                    padx=5, pady=20)

new_Cet_text= ttk.Label(master= input_frame, text= 'New Cet')
new_Cet_text.grid(column= 0, row= 1,padx= 5, pady= 5)                                                            
newCet_label= ttk.Label(master= input_frame)
newCet_label.grid(column= 0,row=2,padx= 5, pady= 5)
#newCet_label['text']= newCet.......moved to update animation function

canvas = FigureCanvasTkAgg(fig, master= show_frame)
canvas.get_tk_widget().grid(column=1,row=0, padx=10)
       
ani = FuncAnimation(fig, update, frames = gen, interval = 300,
                    repeat = False, blit= False)
plt.show()   
        
root.mainloop()


    



    

