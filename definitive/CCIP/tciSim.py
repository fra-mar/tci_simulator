#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 15 10:37:53 2022

@author: paco

choose an option 
"""
import tkinter as tk
from tkinter import ttk

from subprocess import Popen


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("600x300+200+200")
        self.title('TCI simulator. Start menu')
        paddings = {'padx': 5, 'pady': 5}
       
        # initialize data
        self.models = ('Schnider, propofol',
                       'Minto, remifentanil',
                       'Gepts, sufentanil',
                       'Eleveld, propofol')
        self.genders= ('male', 'female')
        
        self.age= tk.DoubleVar(self,  value= 50)
        self.weight= tk.DoubleVar(self, value= 80)
        self.height= tk.IntVar(self, value= 170)
        
        # set up variable
        self.model_var = tk.StringVar(self)
        self.model_var2= tk.StringVar(self)
        self.second_pump= tk.StringVar(self)
        self.gender_var= tk.StringVar(self)

        # create widget
        self.create_widgets()
        
        #create an entry for age, t.ex.
        
        self.a= tk.Entry(self, width= 5, textvariable= self.age)
        self.a.grid(row= 3, column= 1, sticky=tk.W, **paddings)
        
        self.w= tk.Entry(self, width= 5, textvariable= self.weight)
        self.w.grid(row= 4, column= 1, sticky=tk.W, **paddings)
        
        self.h= tk.Entry(self, width=5, textvariable= self.height)
        self.h.grid(row= 5, column= 1, sticky=tk.W, **paddings)
        
        
        self.a_button= tk.Button(self, text='Check values', command= self.option_changed)
        self.a_button.grid(row=7, column=1, rowspan=1, columnspan=2, padx=5, pady= 15, sticky= tk.SW)
        self.start_button= ttk.Button(self, text='Start', 
                                      command= self.start,
                                      state= 'disabled',
                                      )
        self.start_button.grid(row=9, column= 1, sticky=tk.SW, padx=5, pady= 15)
   
    def create_widgets(self):
        # padding for widgets using the grid layout
        paddings = {'padx': 5, 'pady': 5}

        # labels
        label_models = ttk.Label(self,  text='Model, drug. Pump1')
        label_models.grid(column=0, row=0, sticky=tk.W, **paddings)
        
        
        label_models2 = ttk.Label(self, text='Model, drug. Pump2')
        label_models2.grid(column= 0, row= 1, sticky=tk.W, **paddings)

        
        label_age= ttk.Label(self, text='Age(yr)')
        label_age.grid(column=0, row=3, sticky=tk.E, **paddings)
        
        label_weight= ttk.Label(self, text='Weight(Kg)')
        label_weight.grid(column=0, row=4, sticky=tk.E, **paddings)
        
        label_height= ttk.Label(self, text='Height(cm)')
        label_height.grid(column=0, row=5, sticky=tk.E, **paddings)
        
        label_genders = ttk.Label(self,  text='Gender')
        label_genders.grid(column=0, row=6, sticky=tk.E, **paddings)

        # option menus
        model_menu = ttk.OptionMenu(
            self,
            self.model_var,
            self.models[0],
            *self.models,
            command=self.option_changed)
        model_menu.grid(column=1, row=0, sticky=tk.W, **paddings)
        
        activate_pump2= ttk.Checkbutton(
            self,
            command= lambda: model_menu2.configure(state= 'enabled'),
            text= 'Activate',
            variable= self.second_pump,
            onvalue= 'yes',
            offvalue= 'no')
        activate_pump2.grid(column= 2, row=1, sticky=tk.W, **paddings)
        
        model_menu2 = ttk.OptionMenu(
            self,
            self.model_var2,
            self.models[1],
            *self.models,
            command= self.option_changed)
        model_menu2.grid(column=1, row=1, sticky=tk.W, **paddings)
        model_menu2.configure(state= 'disabled')
        
        gender_menu = ttk.OptionMenu(
            self,
            self.gender_var,
            self.genders[0],
            *self.genders,
            command=self.option_changed)
        gender_menu.grid(column=1, row=6, sticky=tk.W, **paddings)

        # output label
        self.output_label = ttk.Label(self, foreground='red')
        self.output_label.grid(column=1, row=7, sticky=tk.W, **paddings)

    def option_changed(self, *args):
        
        output_text=''
        self.output_label['text']= output_text
        
        self.start_button.config(state= 'disabled')
        
        self.m= self.model_var.get()
        self.m2= self.model_var2.get()
        self.a= self.age.get()
        self.w= self.weight.get()
        self.h= self.height.get()
        self.g= self.gender_var.get()
        
        if self.a <0.01 or self.a > 110:
            output_text += 'Valid age 0-110 yr\n'
        if self.w <1 or self.w > 250:
            output_text += 'Valid weight 0-250Kg\n'
        if self.h <20 or self.w > 230:
            output_text += 'Valid height 20-230cm\n'
        else:
            output_text= 'Check the data.\nIf you are sure,\npress START'
            self.start_button.config(state= 'enable')
        
        self.output_label['text']= output_text
        
    def start(self):        
        
        Popen(['python', 'CCIP_main.py',
                        f'{self.m}',
                        f'{self.a}',
                        f'{self.w}',
                        f'{self.h}',
                        f'{self.g[0]}'])
        
        if self.second_pump.get()== 'yes':
            Popen(['python', 'CCIP_main.py',
                            f'{self.m2}',
                            f'{self.a}',
                            f'{self.w}',
                            f'{self.h}',
                            f'{self.g[0]}'])
    

def main():
    
    return App()

if __name__ == "__main__":
    #app = App()
    app= main()
 
    
    app.mainloop()
