# -*- coding: utf-8 -*-
"""
Created on Fri Jul  9 10:39:06 2021

@author: favou
"""
from New_Member_Class import Member_Class

class CR:
    
    def __init__(self, Ned, grade, L, E=210*10**3, A = None, end_connections= 'Pinned-Pinned',  beam_column= 'column',  Method = 'short', serial_number=None, section_type = 'rolled I', finish = None, h=None, b=None, tf=None, tw=None, t_t= None, Iy =None, Iz = None):
        self.Ned = Ned #(kN) Design load
        self.grade = grade
        self.L = L #(m) span of the member 
        self.E = E # N/mm2 Young's modulus
        self.A = A #Area (mm2) 
        self.end_connections = end_connections
        self.beam_column = beam_column
        self.Method = Method
        self.serial_number = serial_number
        self.section_type = section_type
        self.finish = finish        
        
        self.h = h
        self.b = b
        
        self.h_b = self.h/self.b if self.h != None else None
        
        self.tf = tf
        self.tw = tw
        self.t_t =t_t
        
        self.t = max(self.tf, self.tw) if self.tf !=None else 1+1
        
        self.Iy = Iy #mm2
        self.Iz = Iz #mm2
        
        
    
    def I(self):
        """ Second Moment of Area"""
        from My_Functions import member_data_locator
        
        Iy_col = "Second moment of area I Axis y-y cm4"
        Iz_col = "Second moment of area I Axis z-z cm4"

        if self.Method == 'short':
            Iy =  member_data_locator(self.beam_column, self.serial_number, column_heading = Iy_col)*10**4        
            Iz = member_data_locator(self.beam_column, self.serial_number, column_heading = Iz_col)*10**4
        else:
            Iy = self.Iy
            Iz = self.Iz
            
        return [Iy, Iz] # mm^4
    
    
    def Ncr(self ):
        if self.end_connections == 'Pinned-Pinned': #both ends pinned 
            self.rf = 1 # rf = reduction factor
        elif self.end_connections == 'Fixed-Fixed': # both ends fixed 
            self.rf = 0.7
        elif self.end_connections == 'Pinned-Fixed': # one end fixed, other end pinned
            self.rf = 0.85
        elif self.end_connections == 'Fixed-Free':# on end fixed other end free
            self.rf = 2
            
            
        from math import pi
        Iy = CR.I(self)[0]
        Iz = CR.I(self)[1]
        L_cr = self.rf*self.L
        
        Ncr_y = 10**-3*(pi**2 *self.E*Iy)/(L_cr*1000)**2
        Ncr_z = 10**-3*(pi**2 *self.E*Iz)/(self.rf*self.L*1000)**2
            
        return [round(Ncr_y,0), round(Ncr_z,0)]


    def nominal_thickness(self) :
        from My_Functions import member_data_locator
        
   
        #If the beam if from the available database 
        if self.Method == 'short':
            if self.section_type == 'rolled I' or self.section_type == 'welded I':
            
                web_col = 'Thickness of web tw mm'
                tw = member_data_locator(self.beam_column, self.serial_number, column_heading = web_col)
                flange_col = 'Thickness of flange tf mm'
                tf = member_data_locator(self.beam_column, self.serial_number, column_heading = flange_col)
            
                t = max(tw,tf) # nominal thickness
                self.tf = tf
                self.tw = tw
                self.t = t
            
            else:
                print("Hollow section does not have a <short Method>. Change to < CR(self, Method = 'long')>")
        
        elif self.Method == 'long':
            if self.section_type == 'rolled I' or self.section_type == 'welded I':
                t = max(self.tf, self.tw)
            else:
                t = self.t_t
                

        return [t, self.tf, self.tw]
    
    
    def fy(self):
        """ This function returns the fy for the specified beam 
            based on its nominal thickness, t"""
        from pandas import read_excel 
                  
        t = CR.nominal_thickness(self)[0]
        # Determining fy from nominal thickness-fy table 
        df = read_excel('C:/Users/favou/Desktop/Summer Python/Steel_grade.xlsx', sheet_name=0)
        lst = df.values.tolist()
        
        for i in range(len(lst)):
            if self.grade == lst[i][0]:
                if t<=40 :
                    fy = lst[i][1]
                elif t>40 and t<=80:
                    fy = lst[i][3]
        
        return fy 
    
    
    def Area(self):
        """ This function finds the area of the section """
        from My_Functions import member_data_locator
        
     #Finding the crossectional area of the memeber      
        if self.Method == 'short':
            Area_col = 'Area of section cm2'
            Area = member_data_locator(self.beam_column, self.serial_number, Area_col)*10**2 #mm2
       
        elif self.Method == 'long':
            Area = self.A
               
        return round(Area,1)
    
    
    def lda(self):
        """ Non-dimensional slenderness"""        
        try:  
            A = CR.Area(self)
            fy = CR.fy(self)
            Ncr_y = CR.Ncr(self)[0]*10**3
            Ncr_z = CR.Ncr(self)[1]*10**3
               
            from math import sqrt
            lda_y = sqrt(A*fy/Ncr_y)
            lda_z = sqrt(A*fy/Ncr_z)
            return [round(lda_y,2), round(lda_z,2)]
        except:
              print("Name the object 'CR'. i.e. CR = CR(grade = 'S275'....) ")        
    
    
    def buckling_curve (self):
        from My_Functions import member_data_locator
        
        
        lst = ['S235', 'S275', 'S355', 'S420', 'S460'] 
        lst1 = [True for i in lst if i == self.grade]
        a0, a, b, c, d = 0.13, 0.21, 0.34, 0.49, 0.76
            
        if self.section_type == 'rolled I':
            # Finding h_b
            if self.Method == 'short':
                h_col = 'Depth of section h mm'
                h = member_data_locator(self.beam_column, self.serial_number, column_heading = h_col)
                b_col = 'Width of section b mm'
                b1 = member_data_locator(self.beam_column, self.serial_number, column_heading = b_col)
                h_b = h/b1
                tf_col = 'Thickness of flange tf mm'
                tf = member_data_locator(self.beam_column, self.serial_number, column_heading = tf_col)                
                self.h = h
                self.b1 = b1
                self.h_b = h_b
            elif self.Method == 'long':
                h_b = self.h_b
                tf = self.tf


            
            if h_b > 1.2:
                if tf<= 40:
                    if lst1 == [True] :
                        alp_y, alp_z = a, b
                    elif self.grade == 'S460':
                        alp_y, alp_z = a0, a0
                                        
                elif tf > 40 and tf<=100:
                    if lst1 == [True] :
                        alp_y, alp_z = b, c
                    elif self.grade == 'S460':
                        alp_y, alp_z = a, a
                
            if h_b <= 1.2: 
                if tf<= 100:
                    if lst1 == [True] :
                        alp_y, alp_z = b, c
                    elif self.grade == 'S460':
                        alp_y, alp_z = a, a
                                        
                elif tf > 100:
                    if lst1 == [True] :
                        alp_y, alp_z = d, d
                    elif self.grade == 'S460':
                        alp_y, alp_z = c, c 
                                
                
                
        elif self.section_type == 'welded I':
            if self.Method == 'short':
                tf_col = 'Thickness of flange tf mm'
                tf = member_data_locator(self.beam_column, self.serial_number, column_heading = tf_col)                
            elif self.Method == 'long':
                tf = self.tf  
            
            if tf <= 40:
                alp_y, alp_z = b, c
            else:
                alp_y, alp_z = c, d

               
            
                
        elif self.section_type == 'hollow':
            try:
                if self.finish == 'hot':
                   if lst1 == [True] :
                       alp_y, alp_z = a, a
                   elif self.grade == 'S460':
                       alp_y, alp_z = a0, a0
                elif self.finish == 'cold':
                    alp_y, alp_z = c, c
                    
            except:
                print("define finish (<hot> or <cold>) in CR(...finish=... ) ")
        
        return [alp_y, alp_z]
            
    
    def PHI(self):
        alp = CR.buckling_curve(self)
        lda = CR.lda(self)
        PHI_y = 0.5*(1 + alp[0]*(lda[0]-0.2) + lda[0]**2)
        PHI_z = 0.5*(1 + alp[1]*(lda[1]-0.2) + lda[1]**2)
        return [round(PHI_y, 2), round(PHI_z, 2)]
    
    
    def KAI(self):
        from math import sqrt
        PHI = CR.PHI(self)
        lda = CR.lda(self)
        KAI_y = (PHI[0]+sqrt(PHI[0]**2-lda[0]**2))**-1 
        KAI_z = (PHI[1]+sqrt(PHI[1]**2-lda[1]**2))**-1 
        
        KAI_y = 1 if KAI_y>1 else KAI_y
        KAI_z =1 if KAI_z>1 else KAI_z
        
        self.KAI_y = KAI_y
        self.KAI_z = KAI_z
        
        return [round(KAI_y, 2), round(KAI_z, 2)]
    
    
    def CS_res(self):
        Nc_rd = CR.Area(self)*CR.fy(self)*10**-3
        if self.Ned <= Nc_rd:
            return [Nc_rd, "Pass"]
        else:
            return [Nc_rd,"Fail"] 
    
    
    def buck_res_y(self):
        A = CR.Area(self)
        fy = CR.fy(self)
        KAI = CR.KAI(self)
        #Nb_rd_y = KAI[0]*A*fy*10**-3   
        Nb_rd_y = self.KAI_y*A*fy*10**-3   
        
        
        if self.Ned <= Nb_rd_y:
            return [Nb_rd_y,"Pass"]
        else:
            return [Nb_rd_y,"Fail"]           


    def buck_res_z(self):
        A = CR.Area(self)
        fy = CR.fy(self)
        KAI = CR.KAI(self)
        # Nb_rd_z = KAI[1]*A*fy*10**-3   
        Nb_rd_z = self.KAI_z*A*fy*10**-3
        
        if self.Ned <= Nb_rd_z:
            return [Nb_rd_z,"Pass"]
        else:
            return [Nb_rd_z,"Fail"]            
         
        
    def Check(self):
        from My_Functions import underline
        A = CR.Area(self)
        fy = CR.fy(self)
        KAI = CR.KAI(self)
        
        Nc_rd   = CR.Area(self)*CR.fy(self) *10**-3
        # Nb_rd_y = KAI[0]*A*fy*10**-3 #rounded early
        # Nb_rd_z = KAI[1]*A*fy*10**-3 # rounded early
        Nb_rd_y = self.KAI_y*A*fy*10**-3   
        Nb_rd_z = self.KAI_z*A*fy*10**-3
        

##################      Working out  
        print()
        print("")
        print("1) Working out:")   
        print()
        print(f"-A) {underline('Finding Ncr')}")
        
        print(f" --end_conections = {self.end_connections} thus span reduction factor = {self.rf}")
        print(f" --E = {self.E}N/mm2")
        print(f" --Iy = {CR.I(self)[0]}mm4, Iz = {CR.I(self)[1]}mm4")
        
        print()
        print(" -- thus " + underline(f"Ncr-y = {CR.Ncr(self)[0]}kN") + " and " +  underline(f"Ncr-z = {CR.Ncr(self)[1]}kN"))
####################
 
###################    Finding Non-dimensional Slenderness:
        print()    
        print(f"-B) {underline('Finding Non-dimensional Slenderness (lda):')}")
        print()
        print(f" --Area = {CR.Area(self)}mm2")
        if self.section_type == 'hollow':
            print(f" --Nominal thickness = {CR.nominal_thickness(self)[0]}mm assuming uniform thickness ")
        else:
            print(f" --Nominal thickness = {CR.nominal_thickness(self)[0]}mm because tf = {CR.nominal_thickness(self)[1]}mm  and tw = {CR.nominal_thickness(self)[2]}mm")
        print(" -- thus " + underline(f"lda-y = {CR.lda(self)[0]}") + " and " +  underline(f"lda-z = {CR.lda(self)[1]}"))
###################        
        
################### Finding buckling curve
        print()
        print(f"-C) {underline('Finding buckling curve')}")
        print(f" --section_type = {self.section_type}")
        if self.section_type == 'rolled I':
            print(f" --h_b = {round(self.h_b,2)} because h = {self.h}mm, b = {self.b1}mm")
        
        if self.section_type == 'rolled I' or self.section_type == 'welded I':
            print(f" --tf = {self.tf}mm")
        print(f" --steel grade = {self.grade}")
        
        if  self.section_type == 'hollow':
            print(f" --the finish/formed = {self.finish}")

        print(" -- thus " + underline(f"buckling curve(strong axis) = {CR.buckling_curve(self)[0]}") + " and " +  underline(f"buckling curve(weak axis) = {CR.buckling_curve(self)[1]}"))
###################

###################Finding buckling reduction factor(KAI)
        print()
        print(f"-D) {underline('Finding buckling reduction factor(KAI)')}") 
        print(f" --PHI_y = {CR.PHI(self)[0]} and PHI_z = {CR.PHI(self)[1]}")
        print(f" -- thus KAI_y = {CR.KAI(self)[0]} and KAI_z = {CR.KAI(self)[1]} ")
        


###################     
        print()
        print("2) Final verdict:")
        print()
        print(" A) " + f"{underline('Cross-sectional resistance check')}")
        
        if self.Ned >= Nc_rd:
            print(" --Inadequate cross-sectional resistance:")
            print(f""" --{underline("FAILS")} because Ned({self.Ned}kN) >= Nc_rd({round(Nc_rd, 1)}kN)""")
           
        else:
            print(" --Adequate cross-sectional resistance:")
            print(f""" --{underline("PASSES")} because Ned({self.Ned}kN) <= Nc_rd({round(Nc_rd, 1)}kN)""")  
     
        if CR.lda(self)[0] >0.2:
            print()
            print(" B) " + f"{underline('Strong Axis buckling check')}")
            if self.Ned >= Nb_rd_y:
                print(" --Inadequate strong axis (y) buckling resistance:")
                print(f""" --{underline("STRONG Axis: FAILS")} \n 
                      because Ned({self.Ned}kN) >= Nb_rd_y({round(Nb_rd_y, 1)}kN)""")
               
            else:
                print(" --Adequate strong axis (y) buckling resistance:")
                print(f""" --{underline("STRONG Axis: PASSES")} \n 
                      because Ned({self.Ned}kN) <= Nb_rd_y({round(Nb_rd_y, 1)}kN)""")        
        else:
            print()
            print(f""" --The slenderness (strong-axis) is {CR.lda(self)[0]}<=0.2 hence a  
                  member buckling resistance check is not required""")
       
        if CR.lda(self)[1] >0.2:  
            print()
            print(" C) " + f"{underline('Weak Axis buckling check')}")
            if self.Ned >= Nb_rd_z:
                print(" --Inadequate weak axis (z) buckling resistance:")
                print(f""" --{underline("WEAK Axis: FAILS")}\n
                      because Ned({self.Ned}kN) >= Nb_rd_z({round(Nb_rd_z, 1)}kN)""")
                
            else:
                
                print(" --Adequate weak axis (z) buckling resistance:")
                print(f""" --{underline("WEAK Axis: PASSES")} \n
                      because Ned({self.Ned}kN) <= Nb_rd_z({round(Nb_rd_z, 1)}kN)""")        
        else:
            print()
            print(f""" --The slenderness (weak-axis) is {CR.lda(self)[1]}<=0.2 hence a  
                  member buckling resistance check is not required""")        
        
        



#"""Testing """
                            
                            
# CR1 = CR(Ned = 1100, grade='S275', serial_number = '356x406x634', L=1, end_connections = 'Fixed-Free')    
# check = CR1.Check()

#ignore
# ncr = CR1.Ncr()
# ncr1 = CR1.Ncr1()
# print(ncr)
# Area = CR.Area()
# print(Area)
# lda = CR.lda()
# print(lda)
# alp = CR.buckling_curve()
# print(alp)

# phi = CR.PHI()
# print(phi)
# kai = CR.KAI()
# print(kai)

