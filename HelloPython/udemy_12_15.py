print("S12.94 Functions.................................................")
def fun(lst):
    for i in lst:
        print(i)
fun([1,2,3,4])

#........

def avg(a=0,b=0):   # default value set
    print(f"a={a}")
    print(f"b={b}")
    return (a+b)/2
avg(5,10)
avg(b=5,a=10)


#.................Argument passinng function(list | map)
def funArg(a, *args ,**keyWdArg):
    print(a)
    for lstdata in args:
        print(lstdata)

    for key,value in keyWdArg.items():
        print(key,value)

funArg(10, 1, 2, 3, name="kre", age=30)


print("S13.111 Lambda.................................................")
# filter | Map |Reduse ---> predefine lambda function can use in seq list
#with out lambda.........
def quib(x):
    return x**3
print(quib(3))

#with lambda.............
f = lambda x:x**3
print(f(2))

#odd or even find in lambda
def oddEven(x):
    if (x%2==0):
        return "Yes"
    else:
        return "No"
print(oddEven(3))

oddEvenLamda = lambda y: "YesL" if y%2==0 else "NoL"
print(oddEvenLamda(3))

#passing 2 param
f1= lambda a,b: a+b
print(f1(2,3))


#filter -> Use the lambda function to filter the list
lst=[1,2,3,4,5,6]
outlst=list(filter(lambda x:x%2==0,lst) )
print(outlst)

for i in outlst: print(i)

#map -> Use the lambda function to update the list
lst=[2,3,4]
result = list(map(lambda x:x**2,lst) )
print(result)


#reduse -> Use the lambda function to get sum of the list
from functools import reduce
lst=[2,3,4]
sum = reduce(lambda a,b:a+b,lst)
print(sum)


#decorator function, inner function

def decor(fun):
    def inner():
        result = fun()
        return result*2
    return inner

#@decor
def num():
    return 5

resultfun = decor(num)
print(resultfun())


#Genarator.................

def costumgen(x,y):
    while x<y:
        yield x
        x+=1
result = costumgen(10,13)
for i in result : print(i)


# All python keyword
import keyword
print(len(keyword.kwlist))

#['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'breone', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield']


print("S14.126 Modules.................................................")
#Create my own module in [udemy_14_pyModule.py] -User define mod

import udemy_14_pyModule as md
print(md.addM(5,2))
print(md.subM(5,2))

#load without moodule amne

from udemy_14_pyModule import *
print(addM(5,2))
print(subM(5,2))


# pre define python module [Math]
import math as M  
#from math import *

print(M.sqrt(16))
#print(dir(M)) 
#member list on math Module ---> ['__doc__', '__loader__', '__name__', '__package__', '__spec__', 'acos', 'acosh', 'asin', 'asinh', 'atan', 'atan2', 'atanh', 'cbrt', 'ceil', 'comb', 'copysign', 'cos', 'cosh', 'degrees', 'dist', 'e', 'erf', 'erfc', 'exp', 'exp2', 'expm1', 'fabs', 'factorial', 'floor', 'fmod', 'frexp', 'fsum', 'gamma', 'gcd', 'hypot', 'inf', 'isclose', 'isfinite', 'isinf', 'isnan', 'isqrt', 'lcm', 'ldexp', 'lgamma', 'log', 'log10', 'log1p', 'log2', 'modf', 'nan', 'nextafter', 'perm', 'pi', 'pow', 'prod', 'radians', 'remainder', 'sin', 'sinh', 'sqrt', 'sumprod', 'tan', 'tanh', 'tau', 'trunc', 'ulp'


# random --> import
from random import *
for i in range(2):
    print(randint(100,200))
lst=["A","B","C"]
for i in range(2):
    print(choice(lst))



print("S14.132 List Compairation.................................................")
#res=[expression for item in iteration if condition]
lst=[]
for i in range(1,6):
    lst.append(i**2)
print(lst)

lst=[]
lst=[x**3 for x in range(1,6)]
print(lst)


#....................
A=[1,2,3]
B=[5,6,7]
lst3=[]
for i in range(len(A)):
    lst3.append(A[i]*B[i])
print(lst3)

lst3=[]
lst3=[A[i]*B[i] for i in range(len(A))]
print(lst3)

#Find commen element(3,4,5) in both lst
A=[1,2,3,4,5]
B=[7,3,4,5,9]
result=[]
for i in A:
    if i in B:
        result.append(i)
print(result)

# List Compairation...
result=[i for i in A if i in B]
print(result)
