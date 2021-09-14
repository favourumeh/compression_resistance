# -*- coding: utf-8 -*-
"""
Created on Tue Jul 20 13:06:03 2021

@author: favou
"""
from My_Functions import member_data_locator   
import My_Functions as MF
class Member_Class:
    
    def __init__(self, section_shape, Method = 'short', beam_column = 'column', b_cw = 'c', b_cf = 'c', serial_number = None, grade = None, fy_ = None,  h = None, b = None, tf=None, tw=None, r =None, t_RHS =None, d = None, t_CHS = None ):
        self.section_shape = section_shape
        self.Method = Method
        self.beam_column = beam_column
        self.b_cw = b_cw
        self.b_cf =b_cf
        self.serial_number = serial_number
        self.grade = grade
        if self.Method == 'long' and fy_ == None:
            self.fy_ = int(input("What is the fy_ (N/mm2): " ))
        else:
            self.fy_ = fy_
            
        self.h = h
        self.b = b
        self.tf = tf
        self.tw = tf
        self.r = r
        self.t_RHS = t_RHS
        self.d = d
        self.t_CHS = t_CHS
    
    
    def nominal_thickness(self):
            
        
        if self.Method == 'long':
            if self.section_shape == 'I-section':
                self.t = max(self.tw, self.tf)
                
            elif self.section_shape == 'CHS':
                self.t = self.t_CHS
            elif self.section_shape == 'RHS'  :
                self.t = self.t_RHS
        
        elif self.Method == 'short':
            if self.section_shape == 'I-section':
                tf_col = 'Thickness of flange tf mm'
                tf = member_data_locator(self.beam_column, self.serial_number, column_heading = tf_col)                

                web_col = 'Thickness of web tw mm'
                tw = member_data_locator(self.beam_column, self.serial_number, column_heading = web_col)
              
                self.t = max(tw, tf)  
                self.tf = tf
                self.tw = tw
            else:
                print(" nominal_thickness: The short method is not available for CHS or RHS")
                       
        return self.t
    
    
    def fy(self):
        
        """ This function returns the fy for the specified beam 
            based on its nominal thickness, t"""
            
        #if self.Method =='short':
        if self.grade !=None:
            from pandas import read_excel 
                      
            t = Member_Class.nominal_thickness(self)
            # Determining fy from nominal thickness-fy table 
            df = read_excel('C:/Users/favou/Desktop/Summer Python/Steel_grade.xlsx', sheet_name=0)
            lst = df.values.tolist()
            
            for i in range(len(lst)):
                if self.grade == lst[i][0]:
                    if t<=40 :
                        fy = lst[i][1]
                    elif t>40 and t<=80:
                        fy = lst[i][3]
        
#        elif self.Method == 'long':
        elif self.grade == None:
            fy = self.fy_
        
        self.fy_ = fy
        
        return fy
    
    def epsilon(self):
        
        a = Member_Class.fy(self) #line used to access self.fy_
        self.eps = (235/self.fy_)**0.5
        return self.eps
                
    def C_t_I(self):
        
        """ This function defines the Width-to-thickness ratio of an I-section """
        
        if self.section_shape == 'I-section' :
            
            if self.Method == 'short':
                c_t_f_col = 'Ratios for local buckling Flange cf/tf'
                self.c_t_f = member_data_locator(self.beam_column, self.serial_number, column_heading = c_t_f_col)
                
                c_t_w_col = 'Ratios for local buckling Web cw/tw'
                self.c_t_w =  member_data_locator(self.beam_column, self.serial_number, column_heading = c_t_w_col)
               
            elif self.Method == 'long':
                c_w =  self.h -2*self.tf -2*self.r 
                
                c_f = 0.5*(self.b -self.tw -2*self.r)
                
                self.c_t_f = c_f/self.tf
                self.c_t_w = c_w/self.tw
                
            return [self.c_t_f, self.c_t_w]
    

    def C_t_RHS(self):
        call = Member_Class.nominal_thickness(self)
        """ This function defines the Width-to-thickness ratio of a RHS """
        if self.section_shape == 'RHS':
            if self.Method == 'short':
                
                print("C_t_RHS: There is no Method = short for RHS. Define h, b, r and t" )
                
            elif self.Method == 'long':
                c_w =  self.h -2*self.t_RHS -2*self.r 
                
                c_f = self.b -2*self.t_RHS -2*self.r
                
                self.c_t_f = c_f/self.t_RHS
                self.c_t_w = c_w/self.t_RHS
                
            return [self.c_t_f, self.c_t_w]
    
    
    def d_t_CHS(self):
                
        """ This function defines the Width-to-thickness ratio of a CHS """
        if self.section_shape == 'CHS':
            self.d_t = self.d/self.t_CHS
            return self.d_t
    
    
    def width_to_thickness(self):
        """ This function simply calls all the width to thickness functions"""
        a0 = Member_Class.epsilon(self)
        a = Member_Class.C_t_I(self)
        b = Member_Class.C_t_RHS(self)
        c = Member_Class.d_t_CHS(self)
        return [a0, a,b,c]
    
    
    def OF_class(self):
        """ This function determines the class of OUTSTAND FLANGE"""

        call = Member_Class.width_to_thickness(self)
        c_t_u = MF.underline(str(self.c_t_f))
        # print()
        # print(f"--Epsilon = {round(self.eps, 2)}")
        print()
        print("key information for " +  MF.underline('Outstand Flange:')) 
        print()
        print(f"--The width-to-thickness ratio, {MF.underline('c/t')}, is : {c_t_u}")        

        if self.section_shape == "I-section":     
            if self.b_cf == 'c':
                print(f"--For simplicity, it is assumed that the Outstand Flange is in {MF.underline('Compression')}")   
                if self.c_t_f <= 9*self.eps:
                    print('--Outstand flange has' + ' ' + MF.underline('class =' + ' ' + str(1)) + '...\n'
                                 f'... because  c/t <= 9 x epsilon (= {round(9*self.eps, 2)})')
                    return 1
            
                elif self.c_t_f > 9*self.eps and self.c_t_f<=10*self.eps:
                    print('--Outstand flange has' + ' ' + MF.underline('class =' + ' ' + str(2)) + '...\n'
                                 f'... because 9 x epsilon (= {round(9*self.eps, 2)}) < c/t <= 10 x epsilon (= {round(10*self.eps, 2)})')        
                    return 2
                elif self.c_t_f > 10*self.eps and self.c_t_f<=14*self.eps:
                    print('--Outstand flange has' + ' ' + MF.underline('class =' + ' ' + str(3)) + '...\n'
                                 f'... because 10 x epsilon (= {round(10*self.eps, 2)}) < c/t <= 14 x epsilon (= {round(14*self.eps, 2)})')
                    return 3
                else:
                    print('--Outstand flange has' + ' ' + MF.underline('class =' + ' ' + str(4)) + '...\n'
                                 f'... because  c/t > 14 x epsilon (= {round(14*self.eps, 2)})')              
                    return 4         
            else:
               return print(" This tool is not built to handle part subjected to bending")
            
       
    def ICP_class(self):
        call = Member_Class.width_to_thickness(self)
        
        """
            This function determines the class of an Internal Compression Part (ICP)
            given the type of stress acting on the part (b_c: bending(b) or compression (c)) 
            and either the width (c) and thickness(t) or the width-to-thickness ratio (c_t)
        """
        if self.section_shape == 'I-section':
            
            self.c_t = self.c_t_w
        else:
            pass
        
        c_t = self.c_t 
        c_t_u = MF.underline(str(c_t))
        print()
        print("key information for " + MF.underline("ICP:") )
        print()
        print(f"--The width-to-thickness ratio, {MF.underline('c/t')}, is : {c_t_u}")
        if self.b_c == 'b':
            print(f"--Assuming the ICP is in {MF.underline('Bending')}")    
            if c_t <= 72*self.eps:
                print('--ICP has' + ' ' + MF.underline('class =' + ' ' + str(1)) + '...\n'
                              f'... because  c/t <= 72 x epsilon (= {round(72*self.eps, 2)})')
                return 1
        
            elif c_t > 72*self.eps and c_t<=83*self.eps:
                print('--ICP has' + ' ' + MF.underline('class =' + ' ' + str(2)) + '...\n'
                         f'... because 72 x epsilon (= {round(72*self.eps, 2)}) < c/t <= 83 x epsilon (= {round(83*self.eps, 2)})')
                return 2
            
            elif c_t > 83*self.eps and c_t<=124*self.eps:
                print('--ICP has' + ' ' + MF.underline('class =' + ' ' + str(3)) + '...\n'
                         f'... because 83 x epsilon (= {round(83*self.eps, 2)}) < c/t <= 124 x epsilon (= {round(124*self.eps, 2)})')
                return 3
            
            else:
                print('--ICP has' + ' ' + MF.underline('class =' + ' ' + str(4)) + '...\n'
                         f'... because  c/t > 124 x epsilon (= {round(124*self.eps, 2)})')   
                return 4
            
        elif self.b_c == 'c':
            print(f"--Assuming the ICP is in {MF.underline('Compression')}")    
            if float(c_t) <= 33*self.eps:
                print('--ICP has' + ' ' + MF.underline('class =' + ' ' + str(1)) + '...\n'
                     f'... because  c/t <= 33 x epsilon (= {round(33*self.eps, 2)})')
                return 1
            
            elif c_t > 33*self.eps and c_t<=38*self.eps:
                print('--ICP has' + ' ' + MF.underline('class =' + ' ' + str(2)) + '...\n'
                         f'... because 33 x epsilon (= {round(33*self.eps, 2)}) < c/t <= 38 x epsilon (= {round(38*self.eps, 2)})')
                return 2

            elif c_t > 38*self.eps and c_t<=42*self.eps:
                print('--ICP has' + ' ' + MF.underline('class =' + ' ' + str(3)) + '...\n'
                         f'... because 38 x epsilon (= {round(38*self.eps, 2)}) < c/t <= 42 x epsilon (= {round(42*self.eps, 2)})')
                return 3

            else:
                print('--ICP has' + ' ' + MF.underline('class =' + ' ' + str(4)) + '...\n'
                         f'... because  c/t > 42 x epsilon (= {round(42*self.eps, 2)})')    
                return 4        


    def CHS_class(self):
        call = Member_Class.width_to_thickness(self)
        d_t = round(self.d_t, 2)  
        
        d_t_u = MF.underline(str(d_t))
        print()
        print("key information for " + MF.underline("Tubular Section:"))
        print()
        # print(f"--Epsilon = {round(self.eps, 2)}")
        print(f"--The width-to-thickness ratio, {MF.underline('d/t')}, is : {d_t_u}")       

        if d_t <= 50*self.eps**2:
            print('--The tubular section has' + ' ' + MF.underline('class =' + ' ' + str(1)) + '...\n'
                  f'... because  d/t <= 50 x epsilon^2 (= {round(50*self.eps**2, 2)})')
            return 1
    
        elif d_t > 50*self.eps**2 and d_t<=70*self.eps**2:
            print('--The tubular section has' + ' ' + MF.underline('class =' + ' ' + str(2)) + '...\n'
                         f'... because 50 x epsilon^2 (= {round(50*self.eps**2, 2)}) < d/t <= 70 x epsilon^2 (= {round(70*self.eps**2, 2)})')        
            return 2
        
        elif d_t > 70*self.eps**2 and d_t<=90*self.eps**2:
            print('--The tubular section has' + ' ' + MF.underline('class =' + ' ' + str(3)) + '...\n'
                         f'... because 70 x epsilon^2 (= {round(70*self.eps**2, 2)}) < d/t <= 90 x epsilon^2 (= {round(90*self.eps**2, 2)})')
            return 3
        else:
            print('--The tubular section has' + ' ' + MF.underline('class =' + ' ' + str(4)) + '...\n'
                        f'... because  d/t > 90 x epsilon^2 (= {round(90*self.eps**2, 2)})')     
            return 4         


    def classification (self):
        call = Member_Class.width_to_thickness(self)
        call1 = Member_Class.epsilon(self)
        print(f"--Epsilon = {round(self.eps, 2)}")
        print()
        if self.section_shape == 'I-section':
            print( f" {MF.underline('I-section: Web classification')}")
            self.b_c = self.b_cw
            self.c_t = self.c_t_w
            b = Member_Class.ICP_class(self)
            
            print()
            print( f" {MF.underline('I-section: Flange classification')}")
            # self.b_c = self.b_cf
            # self.c_t = self.c_t_f         
            a = Member_Class.OF_class(self)
            c = max(a,b)

            print()
            print('Therefore, the ' + f'{MF.underline( "overall class is " )}' + f'{str(c)}' )
            return c
        
        elif self.section_shape == 'RHS':
            print("RHS : Web classification")
            self.b_c = self.b_cw
            self.c_t = self.c_t_w
            
            a = Member_Class.ICP_class(self)
            print()
            print("RHS : Flange classification")            
            self.b_c = self.b_cf
            self.c_t = self.c_t_f

            b = Member_Class.ICP_class(self)
            
            c = max(a,b)
            print()
            print('Therefore, the ' + f'{MF.underline( "overall class is " )}' + f'{str(c)}' )
            return c  
        
        elif self.section_shape == 'CHS':
            print(f"{MF.underline('CHS Classification:')}")
            c = Member_Class.CHS_class(self)
            print()
            print('Therefore, the ' + f'{MF.underline( "overall class is " )}' + f'{str(c)}' )            
            return c        



# ########## Testing
# M = Member_Class(section_shape ='I-section', grade='S275', serial_number = '152x152x30')

# #M1.classification()

# #print(M.nominal_thickness())
# #A = M.fy()
# # A = M.epsilon()
# # B = M.classification()


# h,b,t_RHS,r = 200,100,16,8
# #M1 = Member_Class(section_shape ='RHS', Method = 'long', fy_ = 355, h=h, b =b, t_RHS = t_RHS, r = r)
# #M1.classification()
# d, t_CHS= 3000, 70

# M2 = Member_Class(section_shape ='CHS', Method = 'long', d=d, t_CHS = t_CHS)
# M2.classification()



        