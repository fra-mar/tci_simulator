#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 17 15:15:58 2022

@author: paco
Script to train how to recieve arguments as a child process
"""
from argparse import ArgumentParser
parser= ArgumentParser()
parser.add_argument( 'model', type=str)
parser.add_argument( 'age', type=float)
parser.add_argument( 'weight', type=float)
parser.add_argument( 'height', type=int)
parser.add_argument( 'gender', type=str)
args=parser.parse_args()

print(args.model)
print(args.age)
print(args.weight)
print(args.height)
print(args.gender)

