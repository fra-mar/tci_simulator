#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 08:31:18 2022

@author: paco

This script calculate pk parameters for a Schnider propofol model
Plasma target
Based on Anesthesioogy 1998;88:1170
"""
def lbm_calc(g,w,h):
    if g=='m':
        lbm= 1.1*w-128*(w/h)**2
    if g=='f':
        lbm= 1.07*w-148*(w/h)**2
    return lbm

weight= 75 #kg
height= 170 #cm
age= 60 #yr
gender= 'm'
lbm= lbm_calc(gender, weight, height)

def schnider_params_calc(a,w,h,lbm):
    #See table 2 in article mentioned above
    vd_central= 4.27 #L
    vd_rapid_peripheral= 18.9-0.391*(a-53) #L
    vd_slow_peripheral= 238 #L
    clearance_met= 1.89 + ((w-77)* 0.0456)+((lbm-59)*-0.0681)+((h-177)*0.0264)
    clearance_rapid_periph= 1.29-0.024*(a-53)
    clearance_slow_periph= 0.836 #all clearances L min-1
    
    #to make integration easier, I calculate elim constants
    k10= clearance_met/vd_central
    k12= clearance_rapid_periph/vd_central
    k21= clearance_rapid_periph/vd_rapid_peripheral
    k13= clearance_slow_periph/vd_central
    k31= clearance_slow_periph/vd_slow_peripheral
    
    schneider_params=(vd_central,
                      vd_rapid_peripheral,
                      vd_slow_peripheral,
                      k10,
                      k12,k21,
                      k13,k31,
                      )
    return schneider_params

params= schnider_params_calc(age,
                              weight,
                              height,
                              lbm)
