#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 08:31:18 2022

@author: paco

This script calculate pk parameters for a Minto remifentanil model
Plasma target
Based on Anesthesiology 1997;86:10-23
"""
def lbm_calc(g,w,h):
    if g=='m':
        lbm= 1.1*w-128*(w/h)**2
    if g=='f':
        lbm= 1.07*w-148*(w/h)**2
    return lbm

#for Minto/remi, keo varies with age linearly
#See Anesthesiology 1997;86: 24, table 1.
keo= lambda age: 0.8781651900711107 -0.007038728622707376*age

def minto_params_calc(g,a,w,h):
    lbm= lbm_calc(g,w,h)
    #See table 3 in article mentioned above
    vd_central= 5.1 - 0.0201* (a-40) + 0.072*(lbm-55) #L
    vd_rapid_peripheral= 9.82 - 0.0811* (a-40) + 0.108*(lbm-55) #L
    vd_slow_peripheral= 5.42 #L
    clearance_met= 2.6 - 0.0162*(a-40) + 0.0191*(lbm-55)
    clearance_rapid_periph= 2.05-0.0301*(a-40)
    clearance_slow_periph= 0.076-0.00113*(a-40) #all clearances L min-1
    
    #to make integration easier, I calculate elim constants
    k10= clearance_met/vd_central
    k12= clearance_rapid_periph/vd_central
    k21= clearance_rapid_periph/vd_rapid_peripheral
    k13= clearance_slow_periph/vd_central
    k31= clearance_slow_periph/vd_slow_peripheral
    ke0= keo(a)
    model= 'Minto'
    drug_name= 'Remifentanil'
    units= (r'$ng\ ml^{-1}$', r'$\mu g\ s^{-1}$')
    ec50=3.
    
    params=[model, 
            drug_name,
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
