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
#from multiprocessing import Pool, Process
import os

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("800x300+10+10")
        self.title('TCI simulator. v1.1. Start menu')
        self.configure(bg= '#f9cb9c')
        paddings = {'padx': 5, 'pady': 5}
        s= ttk.Style()
        s.configure('TMenubutton', background= '#b0ebf4')
        s.configure('TButton', background= '#e69138', foreground= 'black')
       
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
        
        self.start_button= ttk.Button(self, text='CREATE PUMP', 
                                      command= self.start,
                                      state= 'enabled'
                                      )
        self.start_button.grid(row=8, column= 3, 
                               rowspan= 2, 
                               sticky=tk.W, padx=60, pady= 15)
   
    def create_widgets(self):
        # padding for widgets using the grid layout
        paddings = {'padx': 5, 'pady': 5}

        # labels
        label_models = ttk.Label(self,  text='Model, drug.',
                                 background= '#f9cb9c')
        label_models.grid(column=0, row=0, sticky=tk.W, **paddings)
        
        label_age= ttk.Label(self, text='Age (yr)',
                                 background= '#f9cb9c')
        label_age.grid(column=0, row=3, sticky=tk.E, **paddings)
        
        label_weight= ttk.Label(self, text='Weight (Kg)',
                                 background= '#f9cb9c')
        label_weight.grid(column=0, row=4, sticky=tk.E, **paddings)
        
        label_height= ttk.Label(self, text='Height (cm)',
                                 background= '#f9cb9c')
        label_height.grid(column=0, row=5, sticky=tk.E, **paddings)
        
        label_genders = ttk.Label(self,  text='Gender',
                                 background= '#f9cb9c')
        label_genders.grid(column=0, row=6, **paddings)
        
        doThis='''
        1. Choose model, age, weight, height and sex.
        2. Click on 'CREATE PUMP'. 
        3. A pump (paused) will be displayed.
        4. Create as many pumps as you wish.
        5. Rearrange the pumps in your screen.
        6. Click on each pump's START button.
        7. Use UP and DOWN buttons to select Cet.
        8. Click on SET to confirm the new Cet.
        9. SAVE creates a file with the simulated data.
        '''
        label_doThis= ttk.Label(self, text= doThis,
                               background= '#f9cb6f',
                               foreground='black',
                               font= ('Cambria',10),
                               justify= 'left')
        label_doThis.grid(column= 3, row= 3,
                          sticky= 'e',
                          columnspan= 2,
                          rowspan= 4, padx= 50)
        info='Not for clinical use. Free to distribute. Francisco Martinez Torrente. May 2023'
      
       
        label_info= tk.Label(self,  text= info,
                                 background= '#f9cb9c',
                                 foreground= '#38761d',
                                 font= ('Cambria',8))
        label_info.grid(column=0, 
                        columnspan=5,rowspan=2, row=10, sticky=tk.SW, **paddings)

        # option menus
        
        model_menu = ttk.OptionMenu(
            self,
            self.model_var,
            self.models[0],
            *self.models)
        model_menu.grid(column=1, row=0, sticky=tk.W, **paddings)
        
      
        gender_menu = ttk.OptionMenu(
            self,
            self.gender_var,
            self.genders[0],
            *self.genders)
        gender_menu.grid(column=1, row=6, sticky=tk.W, **paddings)

        # output label
        self.output_label = ttk.Label(self, foreground='red')
        self.output_label.grid(column=1, row=7, 
                               columnspan= 2, 
                               sticky=tk.W, **paddings)

    
    '''
    def run_CCIP(self, m,a,w,h,g):
        with open('init_params.txt', 'w') as f:
            f.write(f'{m},{a},{w},{h},{g}')
        os.system("python CCIP_main.py")
    '''    
    def start(self):  
        self.m= self.model_var.get()
        
        self.a= self.age.get()
        self.w= self.weight.get()
        self.h= self.height.get()
        self.g= self.gender_var.get()
        '''args1=(self.m, 
                self.a,
                self.w,
                self.h,
                self.g[0])
        
        if self.second_pump.get()== 'yes':
            p1= Process(target= self.run_CCIP, args= args1)
            p2= Process(target= self.run_CCIP, args= args2)
            p1.start()
            p2.start()
            p1.join()
            p2.join()  
        else:    
            p1= Process(target= self.run_CCIP, args= args1)
            p1.start()
            p1.join() 
        '''
        
        with open('init_params.txt', 'w') as f:
            f.write(f'{self.m},{self.a},{self.w},{self.h},{self.g[0]}')
        
        #to be used for final compilation linux
        #path= os.path.join('dist','CCIP_main','CCIP_main')  
        #Popen([f'{path}'])
        
        #to be used for final compilation windows
        #path= os.path.join('dist','CCIP_main','CCIP_main.exe') 
 	#Popen([f'{path}']

        #to be used while developing
        path= ['python','CCIP_main.py']
        Popen(path)
        
       
            

if __name__ == "__main__":
    app = App()
    
    app.mainloop()
