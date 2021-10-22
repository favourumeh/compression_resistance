# -*- coding: utf-8 -*-
"""
Created on Fri Oct 22 13:57:43 2021

@author: favou
"""

from Automating_Comprssion_Resistance_I_section import Auto_I_section 


#################### Change these variables accordingly ######################

Ned = 1300 # design load in kN
L = 4 # span of the structural memeber in metres(m)

# specify if the structural memeber is a universal beam or column
beam_column = 'column'  # options: 'beam' or 'column' 

grade = 'S235' #steel grade. options: 'S235', 'S275', 'S355', 'S450'
E = 210000 # young's modulus of the steel
end_connections = 'Pinned-Pinned'  # options: 'Pinned-Pinned', 'Fixed-Fixed', 'Pinned-Fixed', 'Fixed-Free' 


#keep b_cw and b_cf set to 'c' for compression
    # is the web of the structural memeber in bending or compression
b_cw = 'c' #  options: 'c' for compression or 'b' for bending

     # is the flange of the structural member in bending or compression
b_cf ='c'  # options: 'c' for compression or 'b' for bending

###############################################################################


A = Auto_I_section(Ned=Ned, L=L, grade=grade, end_connections= end_connections, E = E, beam_column = beam_column, b_cw = b_cw, b_cf = b_cf)

A.iteration()