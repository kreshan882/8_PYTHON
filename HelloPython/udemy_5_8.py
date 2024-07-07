###############################
#S5  Special  Type         ####
###############################
#py udemy_4_.py
print("S5.45..............................................")

def m1():
    a=10

print(m1())   #None  (not return anythink)

PI=3.12
FINAL_VAL=200  #define constants [UPPERCASE variable name]

str="abc"
str=None
str="xxx"
print(str)

w=10
#del w
print(w) #NameError: name 'w' is not defined

print("S6.50 Arithmetic operator..............................................")

a,b=10,5
print(a**b) #100000
print(a<=b) #False


print("S7.55 Input/Output Functionr..........................................")
"""
name="kresh"
marks=94.5678
print(name,marks,sep='|')   #kresh|94.5678
print("Name is:",name," Marks are:",marks)       #Name is: kresh  Marks are: 94.5678
print("Name is:%s, Marks are:%.3f"%(name,marks)) #Name is:kresh, Marks are:94.568
print("Name is:{}, Marks are:{}".format(name,marks)) #Name is: kresh  Marks are: 94.5678
print("Name is:{0}, Marks are:{1}".format(name,marks))

#RUN IN TERMINAL
s=input("Enter name:")
print(s)
i=int(input("Enter Age:"))  #if not int exception
print(i)


lst=[x for x in input("Ent 3 number, with comma seperator:").split(',')]  #1,2,3
print(lst)   #['1', '2', '3']

lst=['A','B','C','D','E']
print("Pick 3 of this:",lst)

in_lst=[x for x in input("Pick 3 of this, with comma seperator:").split(',')]
print("Total count:%s, Total Amount:%.2f"%(len(in_lst), (len(in_lst)*5.0)))
"""
print("S8.60 More program..................................................")

a,b,c=[int(x) for x in input("Enter 3 number, with space seperate").split()]
avg=(a+b+c)/3
print("Average:%.3f"%(avg))

#.....
stuId=int(input("ent id:"))
stuName=input("ent name:")
stuMark=float(input("ent mark:"))
print("Id:",stuId," Name:",stuName," Mark:",stuMark)

#.....inbuild MODULES
import math
r=float(input("enter circle redias:"))
area=math.pi* r**2
print("Area is:",area)  #Area is: 78.53981633974483

print("S9.64 Flow Control Statement.....next page")
