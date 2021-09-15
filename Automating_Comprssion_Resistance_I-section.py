# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 11:58:49 2021

This script determines the most efficient(minimum section area) I-section size required for a given load Ned

@author: favou
"""
from Class_and_Compression_tool import CR 
from Class_and_Compression_tool import Member_Class
from My_Functions import any_True
from My_Functions import searching_df_columns
from My_Functions import member_data_locator
from My_Functions import underline


class Auto_I_section:
    grades = ['S235', 'S275', 'S355', 'S450']
   
    def __init__(self, Ned, L, grade, E = 210000, beam_column = 'column', b_cw = 'c', b_cf ='c'):
        
        self.Ned = Ned #Design load in KN
                   
        self.grade = grade #grade of steel ( any one in the list in line 18)
        self.L =L #span of member(beam/column) in m
        self.E = E #young's modulus of member in N/mm2 or MPa
        
        self.b_cw = b_cw #is the web in bending or compression (b_cw = "b" is bending, b_cf = "c" is compression)
        self.b_cf = b_cf #is the flange in bending or compression (b_cw = "b" is bending, b_cf = "c" is compression)
        
        self.beam_column = beam_column # is the member a beam or a column (beam_column = "beam" means member is a beam...). 
        
        if any_True(self.grade, Auto_I_section.grades) == False :
            " if the grade inputted is not part of database "
            
            self.grade= input(f" The grade inputted is not one of {Auto_I_section.grades}. Please choose one: ")
        
    
    def grade_to_fy(self):
        
        """ 
        
        This function generates an initial estimate of the fy from the grade. Can change when the 
        nominal thickness is defined.
        
        """
        
        if self.grade != None:
            
            if self.grade == 'S235':
                self.fy = 235
            elif self.grade == 'S275':
                self.fy = 275
            elif self.grade == 'S355':
                self.fy = 355
            elif self.grade == 'S450':
                self.fy= 450
            
            return self.fy
            
    def Area(self):
        
        call = Auto_I_section.grade_to_fy(self)
        k = 0.4
        self.Area = 10*self.Ned/(k*self.fy) # Sizing column (Generating an area estimate (cm2))
        
        return self.Area

    def serial_number_generator(self):
        call = Auto_I_section.Area(self)
        """ Takes in the type of member (beam or column), its serial number and some 
            words in its heading (doesn't have to be all) and extracts the relevant 
            property for a beam/column for that serial number """
            

        UKC_dir = 'Merged UKC.xlsx'
        UKB_dir = 'Merged UKB.xlsx'
        column_heading = 'Area of section cm2'
        serial_heading = 'Designation Serial size'
        from pandas import read_excel 
        if self.beam_column == 'column':
            df = read_excel (UKC_dir)
            
        elif self.beam_column == 'beam':
            df = read_excel (UKB_dir)               
        
        
        data_col = searching_df_columns(df, column_heading)
        serial_col = searching_df_columns(df, serial_heading)
        df1 = df.sort_values(data_col)
        df1.index = [i for i in range(len(df1.index))]
        
        found =0
        i = -1
        self.Serial_Number_lst = []
        while found < 4:
            i +=1
            Section_Area = df.loc[i, data_col]
            if Section_Area >= self.Area:
                found +=1
                self.Serial_Number_lst.append(df1.loc[i, serial_col])
                
        return self.Serial_Number_lst
        
    def iteration(self):
        call = Auto_I_section.Area(self)
        
        """ This function determines the iterates through the UKC or
             UKB database to find the smallest member (Area-wise)that can 
             support a given compressive load against squash(cross-sectional
              resistance) and buckling(member buckling resistance)"""
            

        UKC_dir = 'Merged UKC.xlsx'
        UKB_dir = 'Merged UKB.xlsx'
        column_heading = 'Area of section cm2'
        serial_heading = 'Designation Serial size'
        from pandas import read_excel 
        if self.beam_column == 'column':
            df = read_excel (UKC_dir)
            
        elif self.beam_column == 'beam':
            df = read_excel (UKB_dir)               
        
        
        data_col = searching_df_columns(df, column_heading)
        serial_col = searching_df_columns(df, serial_heading)
        df1 = df.sort_values(data_col)
        df1.index = [i for i in range(len(df1.index))]
        
        i = -1
        self.Serial_Number_lst = []
        
        A = 'Fail'
        k =0
        while A == "Fail":
            i +=1
            Section_Area = df1.loc[i, data_col]

            if Section_Area >= self.Area:
                k+=1         
                serial_number = df1.loc[i, serial_col]
                print()
                print(f" Member {k}: {serial_number}")
                print()                       
                A = Auto_I_section.Compression_Resistance(self, serial_number) 
                
        #Working out 
        self.C.Check()
        

        
    def nominal_thickness(self):
        tf_col = 'Thickness of flange tf mm'
        tf = member_data_locator(self.beam_column, self.serial_number, column_heading = tf_col)                

        web_col = 'Thickness of web tw mm'
        tw = member_data_locator(self.beam_column, self.serial_number, column_heading = web_col)
      
        self.t = max(tw, tf)  
        self.tf = tf
        self.tw = tw 
        
        return self.t
     
    
    def fy(self):
        
        """ 
            This function returns the fy for the specified beam 
            based on its nominal thickness, t
            
        """
            
        from pandas import read_excel 
                  
        t = Auto_I_section.nominal_thickness(self)
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

    def epsilon(self):
        
        call = Auto_I_section.fy(self) #line used to access self.fy_
        self.eps = (235/self.fy)**0.5
        return self.eps
    
    def C_t_I(self):
        
        """ This function defines the Width-to-thickness ratio of an I-section """
    

        c_t_f_col = 'Ratios for local buckling Flange cf/tf'
        self.c_t_f = member_data_locator(self.beam_column, self.serial_number, column_heading = c_t_f_col)
        
        c_t_w_col = 'Ratios for local buckling Web cw/tw'
        self.c_t_w =  member_data_locator(self.beam_column, self.serial_number, column_heading = c_t_w_col)

    def width_to_thickness(self):
        """ This function simply calls the width to thickness functions"""
        a0 = Auto_I_section.epsilon(self)
        a =  Auto_I_section.C_t_I(self)
    
    
    def Classification(self, serial_number):
        self.serial_number = serial_number
        call = Auto_I_section.fy(self) #line used to access self.fy
        b_cw = self.b_cw # web in bending ('b') or compression ('c')
        b_cf = self.b_cf # # flange in bending ('b') or compression ('c')
        fy = self.fy #(N/mm2) yield stress (if unsure leave this as: fy = None)
        
        M = Member_Class(section_shape = 'I-section', b_cw = b_cw, b_cf = b_cf, fy_ = fy, serial_number = serial_number)
        
        Class = M.classification()
        return Class
    
    def Compression_Resistance(self, serial_number):
        self.serial_number = serial_number
        Ned = self.Ned #(kN) Design load
        grade = self.grade # 'S235', 'S275', 'S355', 'S450' 
        L = self.L #(m) span of the member 
        E = self.E # (N/mm2) Young's modulus
        end_connections = 'Pinned-Pinned' # 'Pinned-Pinned', 'Fixed-Fixed', 'Pinned-Fixed', 'Fixed-Free' 
        section_type = 'rolled I' # 'rolled I' (I-section), 'welded I' (I-section), 'hollow'
        
        self.C = CR(Ned=Ned, grade =grade, L = L, E = E, end_connections = end_connections, section_type = section_type, serial_number=serial_number)     
        
        a0 = self.C.CS_res()
        a1 = self.C.buck_res_y()
        a2 = self.C.buck_res_z()
        
        lst = [a0[1], a1[1], a2[1]]
        if lst == ['Pass' for i in range(3)]:
            print()
            print(f"-- {underline('FINAL VERDICT')}: SUCCESS")
            print(f"    The section {serial_number} PASSES all check:")
            print(f" 1) Cross-sectional Resistance: {a0[1]}. Ned = {self.Ned}kN, Ncrd = {round(a0[0], 2)}kN ")
            print(f" 2) STRONG AXIS Member Buckling Resistance: {a1[1]}. Ned = {self.Ned}kN, Nb_rd_y = {round(a1[0],2)}kN ")
            print(f" 3) WEAK AXIS Member Buckling Resistance: {a2[1]}. Ned = {self.Ned}kN, Nb_rd_z= {round(a2[0],2)}kN")
            return "Pass"
        else:
            print()
            print(f"-- {underline('FINAL VERDICT')}: FAILURE")
            print(f"    The section {serial_number} FAILED atleast one design check.")
            print(f" 1) Cross-sectional Resistance: {a0[1]}. Ned = {self.Ned}kN, Ncrd = {round(a0[0],2)}kN")
            print(f" 2) STRONG AXIS Member Buckling Resistance: {a1[1]}. Ned = {self.Ned}kN, Nb_rd_y = {round(a1[0],2)}kN")
            print(f" 3) WEAK AXIS Member Buckling Resistance: {a2[1]}. Ned = {self.Ned}kN, Nb_rd_z= {round(a2[0],2)}kN")                
            return "Fail"

    
    

    
###########################  Testing  ########################################
# A = Auto_I_section(Ned =305.6, L=4.5, grade = 'S275')  


# B = A.iteration()

A = Auto_I_section(Ned =1100, L=4, grade = 'S275')  


B = A.iteration()


##grade
##fy (derived from steel grade or written manually])
##Ned 
##Area (derived from Ned/fy  = A)
##Assume class 1-3 then check that memeber is class 1-3
##sort Area column from smallest to largest then iterate until the section chosen
##satisfies all design checks cross-sectional and buckling resistance 

#class CR_A()
