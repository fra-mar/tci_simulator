#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 08:31:18 2022

@author: paco

This script calculate pk parameters for a Eleveld Propofol model

Based on BJA 2018:120:887
"""
import numpy as np

#FreeFatMass calculator after Al-Sallami
def ffm(g,a,w,h):
    
    bmi= w/((h/100)**2)
    if g== 'm':
        r= (0.88+ ((1-0.88)/(1+(a/13.4)**(-12.7))))*(9270*w/(6680+216*bmi))
    elif g== 'f':
        r= (1.11+ ((1-1.11)/(1+((a/7.1)**(-1.1)))))*(9270*w/(8780+244*bmi))
    
    return r 
#%% Model parameters
t1= 6.28
t2= 25.55
t3=273
t4= 1.79
t5= 1.75 
t6= 1.11
t7= 0.191
t8= 42.30 
t9= 9.06
t10= -0.0156
t11= -0.00286
t12= 33.6
t13= -0.0138
t14= 68.3 
t15= 2.10 
t16= 1.30 
t17= 1.42 
t18= 0.68
e1= 0.610
e2= 0.565
e3= 0.597
e4= 0.265
e5= 0.346
e6= 0.209
e7= 0.463
#%%lambdas



#%%
def eleveld_params_calc(g,a,w,h):
    
    f_ageing= lambda x: np.exp(x*(a-35))
    Ce50= t1 * f_ageing(t7)*np.exp(e1)
    f_sigmoid= lambda x, E50, l: x**l/(x**l + E50**l)
  
    f_central= lambda x: f_sigmoid(x,t12,1)
    f_cl_maturation=  f_sigmoid(a*52+40,t8,t9)
    f_cl_maturation_ref= f_sigmoid(35*52,t8,t9)
    quot_cl_mat= f_cl_maturation/f_cl_maturation_ref
    
    f_q3_maturation=  f_sigmoid(a*52+40, t14,1)
    f_q3_maturation_ref= f_sigmoid(35*52 + 0.77, t14, 1)
    quot_f_q3_mat= f_q3_maturation/f_q3_maturation_ref
    
    f_opiates= lambda x: 1#np.exp(x*a) #assume always opioids, otherwise 1
    
    vd_central= t1* f_central(w)/f_central(70) * np.exp(e1)
    vd_rapid_peripheral= t2* f_ageing(t10)*np.exp(e2)* (w/70)
    vd_slow_peripheral= t3*  ffm(g, a, w, h)/ffm('m',35,70,170)* f_opiates(t13)*np.exp(e3)
    
    if g== 'm':
        theta= t4
    elif g== 'f':
        theta= t5
    cl= theta* ((w/70)**0.75) * quot_cl_mat* f_opiates(t11)*np.exp(e4)
    q2= t5*((vd_rapid_peripheral/25.5)**0.75)* (1+ t6* (1- f_q3_maturation))* np.exp(e5)
    q3= t6*((vd_slow_peripheral/273)**0.75)* quot_f_q3_mat * np.exp(e6)
    
    k10= cl/vd_central
    k12= q2/vd_central
    k21= q2/vd_rapid_peripheral
    k13= q3/vd_central
    k31= q3/vd_slow_peripheral
    
    ke0= 0.146 #arterial value. The make a difference with venous.
    model= 'Eleveld'
    drug_name= 'Propofol'
    units= (r'$\mu g\ ml^{-1}$', r'mg$\ s^{-1}$')
    ec50= 3.
    
    params=[drug_name, 
            model,
            units, ec50,
            vd_central,
            vd_rapid_peripheral,
            vd_slow_peripheral,
            k10,
            k12,k21,
            k13,k31,
            ke0
            ]
    return params
