# -*- coding: utf-8 -*-
"""
Created on Sat Jul 24 18:38:11 2021

@author: favou
"""

""" Fill in the all the important properties and run script"""

from New_Member_Class import Member_Class

from compression_resistance import CR


""" 1) Required Properties """
Method = 'long' # 'short'(using beam/column database), 'long'(manually add b/c propoerties)
section_shape = 'RHS' # 'I-section', 'RHS', 'CHS'
b_cw = 'c' # web in bending ('b') or compression ('c')
b_cf = 'c' # # flange in bending ('b') or compression ('c')
fy_ = None #(N/mm2) yield stress (if unsure leave this as: fy_ = None)

"""1.1) Specific to Compression Resistance"""
Ned = 748 #(kN) Design load
grade = 'S355' # 'S235', 'S275', 'S355', 'S450' 
L = 5 #(m) span of the member 
E = 210*10**3 # (N/mm2) Young's modulus
end_connections = 'Pinned-Pinned' # 'Pinned-Pinned', 'Fixed-Fixed', 'Pinned-Fixed', 'Fixed-Free' 
section_type = 'hollow' # 'rolled I' (I-section), 'welded I' (I-section), 'hollow'
finish = 'hot' # 'hot' finished, 'cold' formed     (hollow section)  



""" 2) Specify if Method = 'short' (only for I-section)"""
serial_number = '152x152x30'
beam_column = 'column' # is the member a: 'column' or 'beam' 


""" 3) Specify if Method = 'Long' """   
     

""" 3.1) ... and I-section"""
tf = 9.4 #(mm) flange thickness (for I-section)
tw = 6.5 #(mm) web thickness (for I-section)


""" 3.2)... and  I-section or RHS"""
h = 200 #(mm)  height of section
b = 100 # (mm) width of section
r = 8 #(mm) radius of curvature


""" 3.3) ... and RHS"""
t_RHS = 16 #(mm) Thickness of RHS


""" 3.4) ... and CHS"""
d = 150 # (mm) outer diameter of CHS
t_CHS = 10 #(mm) thcickness of CHS


""" 3.5) Specific for compression resistance"""
A = 8300 #(mm2) Cross-sectional Area 
Iy = 36780000 #(mm4) strong axis(y) 2nd moment of area
Iz = 11470000 #(mm4) weak axis(z) 2nd moment of area
    
#t_t = t_RHS #(mm) thickness (uniform) of hollow section 

if section_shape == 'RHS':
    t_t = t_RHS 
else:
    t_t =t_CHS







#checks 


# MC = Member_Class(section_shape, Method, beam_column, b_cw, b_cf, serial_number, grade, fy_, h, b, tf, tw, r, t_RHS, d, t_CHS)
# CR1 = CR(Ned, grade, L, E, A, end_connections,  beam_column,  Method, serial_number, section_type, finish, h=h, b=b, tf=tf, tw=tw, t_t=t_t, Iy=Iy, Iz=Iz)

# A = MC.classification()
# CR1.Check()