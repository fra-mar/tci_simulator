#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 08:31:18 2022

@author: paco

This script calculate pk parameters for a Schnider propofol model
Plasma target
Based on StanPump software/ Gepts E, Anesthesiology 1995;83:1194
Didn't found any covariate

"""


def sufenta_params_calc():
    #See table 2 in article mentioned above
    vd_central= 16.6 #L
    vd_rapid_peripheral= 72 #L
    vd_slow_peripheral= 398 #L
    clearance_met= 0.90  #L min-1
    clearance_rapid_periph= 1.4
    clearance_slow_periph= 0.36
    
    #to make integration easier, I calculate elim constants
    k10= clearance_met/vd_central
    k12= clearance_rapid_periph/vd_central
    k21= clearance_rapid_periph/vd_rapid_peripheral
    k13= clearance_slow_periph/vd_central
    k31= clearance_slow_periph/vd_slow_peripheral
    ke0= 0.119
    drug_name= 'Sufentanyl'
    model= 'Gepts'
    units= (r'$ng\ ml^{-1}$', r'$\mu g\ s^{-1}$')
    ec50= 0.23
    
    params=[drug_name,
            model,
            units,ec50,vd_central,
            vd_rapid_peripheral,
            vd_slow_peripheral,
            k10,
            k12,k21,
            k13,k31,
            ke0
            ]
    return params

