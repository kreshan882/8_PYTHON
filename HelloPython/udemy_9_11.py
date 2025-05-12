print("S9.64 Flow Control Statement.................................................")
# if | while,fore| break, continue,pass, retuen


x=2
if x==0:
    print(x," is zero")
elif x%2==0:
    print(x," is even")
else :
    print(x," is odd")    

#....
maths=36
physics=90
chemistry=40
if(maths>=35 and physics>=35 and chemistry>=35):
    print("Pass")
    print("Grade",(maths+physics+chemistry)/3)
else:
    print("Failed")

#.......
x=2
y=10

if x%2==0: x+=1
while x<=y:
    print("odd numbers",x)
    x+=2

#...S9.73...........cont...

for x in range(50,61,2):
    print(x)


#.....
lst=[1,2,3,4]
fibanachi=1
for i in lst:
    fibanachi*=i
print("Fibanachi 4 is:",fibanachi)

#...77 break continue (3 skip, 5 break)
x=0
while x<20:
    x+=1
    if(x==3): continue
    if(x==5): break
    print(x)

# asserts(true/false) ,like junit...
x=11
assert x>10, "wrong number entered"  # give exception with desctiption
print("True value:",x)

#79..
#l1=eval(input("Enter list of element:"))
L1=[1,2,3,4, 2,3]
L2=[]
for each_val in L1:
    if each_val not in L2:
        L2.append(each_val)
print("Simular to Set:",L2)

#80 prigram 1...
in_word="abcdebc"
find_char_vowel={'a','b','c'}
result_map={}

for c in in_word:
    if c in find_char_vowel:
        result_map[c]=result_map.get(c,0)+1

for k,v in result_map.items():
    print("key char:",k,"  count:",v) #a-1,b-2,c-2

#81 prigram 2...
n =int(input("enter no of employee:"))
empp_map={}
for i in range(n):
    name=input("Emp Name:")
    salary=input("Emp Salary:")
    empp_map[name]=salary

while True:
    name=input("Which Emp Sal Need? ")
    salary = empp_map.get(name,-1)
    if salary == -1:
        print("Emp not avaliable")
    else:
        print("The Salary of emp is:",salary)

    choice = input("Do u need to Continuee[Y|N]:")
    if choice=="N":
        break

#.................


x=int(input("EnterNumber:"))
i=0
while i<x:
    i+=1
    if(i%10==0): continue
    if(i>35): break
    print(i)
    


print("S10.82 More Program.................................................")

s='-'.join(['a','b','c'])
print(s)   #a-b-c

s1="kreshan"
print(s1[::-1])  # reversed-> nahserk
print(''.join(reversed(s1)))  # reversed & convert to string-> nahserk

# reverse sentance.................................
s3="my name is kreshan"
temp =s3.split()
print (temp)  # array ['my', 'name', 'is', 'kreshan']
result =[]
i=len(temp)-1
while i>=0:
    result.append(temp[i]) # reversal array hear
    i= i-1

output=' '.join(result)
print(output)  #kreshan is name my

# remove duplicate.................................
r="sssddeeddss"
temp=[]
for s in r:
    if s not in temp:
        temp.append(s)
print(temp)    #['s', 'd', 'e']
print(''.join(temp))  #sde


# character count map/dictonary.................................

s="aaabbcddd"
dict ={} # dictonary map
for c in s:
    if c in dict.keys():
        dict[c] = dict[c]+1
    else:
        dict[c] =1

for k,v in dict.items():
    print("{}={} ".format(k,v)  ,end="")  # end--same line --> a=3  b=2 c=1 d=3

# pramit print.................................
print()
n=5
for i in range(1,n+1):
    print("* "*i)
   
#*
#* *
#* * *
#* * * *
#* * * * *


# find substring possion[DDD].................................
s="hi DDD my name DDDis kreshDDDna"
pos=-1
while True:
    pos=s.find("DDD",pos+1,len(s))
    if pos == -1:
        break
    print("substring location:",pos) # 3 5 26
    found=True
if found== False:
    print("substring not found")


print("S11.92 comment line argument.................................................")
#py .\udemy_9_.py 111 222
#import sys
#lst =sys.argv
#for i in lst:
#    print(i,end=" ") #.\udemy_9_.py 111 222
#print(len(lst)) #3

#Atm System
import sys

print("ATM: Initial Balance: 10000")
amount = 10000
print("\nChoose Option: \n"
      "1. Check balance\n"
      "2. Withdraw\n"
      "3. Deposit Cash\n"
      "4. Deposit Cheque\n")

lst = sys.argv
lst = ["111","222"]

if int(lst[1]) == 1:
    print(amount)
elif int(lst[1]) == 2:
    withdraw = int(input("Enter amount of money to be withdrawn: "))
    print(amount - withdraw)
elif int(lst[1]) == 3:
    deposit = int(input("Enter amount of money to deposit: "))
    print(amount + deposit)
elif int(lst[1]) == 4:
    deposit = int(input("Enter amount of money to deposit: "))
    print(amount + deposit)
else:
    print("Invalid Command")
