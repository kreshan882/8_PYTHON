""" my first project """
# print('comments1')

"""
print('Hello, world!22')
x=int(input("enter min Num"))
y=int(input("enter max Num"))
i=x
if i%2==0: i=x+1
while i<=y:
    print(i)
    i+=2
print('start..') 
"""

#S3 ##############################
"""
print(e)
print(type(e))


a=0XFF
print(a)
print(type(a))

numberif=10

print(int("123"))

First_name='raj'
age=33
hight=175.5
print(First_name)
"""

###############################
#S4  Sequence Type         ####
###############################

s="""kreshan  
trrr"""
print(s,":",s[2]) # concat " , "
print(s[0:3])
print(s[0:6:2]) #0 to 6 and jupu each 2
print(s[7::-1]) #reverse order 
print(s*2)
print(len(s))


print("S4.28 Stript......................................")
print(s.strip())  # trim remove pre post space
print(s.find("sh",0,len(s))) # substring location, not founf -1
print(s.replace("shan","0000000"))

print("S4.30 List(mutable)......................................")
lst=[2,3.10, True ,"listString",-10]
print(lst)
print(lst[1])
print(lst[1:3])

lst.append("newStr")
lst.remove("listString")
del(lst[1])
lst.insert(1,999)
print(lst)  #[2, True, -10, 'newStr']

nlst=[3,5,20.5,-10, 30]
print(min(nlst)) # of all number it will print
nlst.sort(reverse=True)
print(nlst)

print("S4.33 Tuple(immuatable list)......................................")

tpl=(10,20,30,20,'kkk')  #tpl=(10,)
print(type(tpl))
print(tpl)
#tpl[2] =1111  # TypeError: 'tuple' object does not support item assignment
print(tpl.count(20))
print(tpl.index('kkk'))

print("S4.35 List to Tuple..............................................")

lst1=[3,7,'kk']
print(type(lst1))
tpl2=tuple(lst1)
print(type(tpl2))

print("S4.37 Set..............................................")
s={1,2,"xxx",2,3}
s.add(5)           #{1,2,"xxx",3,5}
s.update([98,99])  #{1,2,"xxx",3,5  ,98,99}
s.remove(99)       #{1,2,"xxx",3,5  ,98}
print(s)

f=frozenset(s)
#f.remove(2) #frozen set is immutable

print("S4.39 range..............................................")
r=range(1,15,3)  # 1 to 50 , then StepJump 3
for i in r:
    print(i)  # 1 4 7 10 13

print("S4.40 bytearray..............................................")
lstk=[2,3,4,55]
b=bytes(lstk)
ba=bytearray(lstk)
ba[2]=33   # only byte array can update | byes can not update


print("S4.41 dictionary:: MAP........................................")
dict={1:"aaa",2:"bbbb",3:"ccc"}
print(dict)
print(dict.items())

k=dict.keys()
for i in k:print(i)  # 1, 2 ,3

v=dict.values()
for i in v:print(i)  #aaa, bbb,cccc

del dict[1]
print(dict)   # {2: 'bbbb', 3: 'ccc'}


print("S4.42 immutability(memort location)........................................")
a=10
b=10
print(id(a))  #140732915325656
print(id(a))  #140732915325656   (both [10] are in same memory location)
print(a is b) #True  (special in pythin |string, numbe,boolean same behavior)


print("S4.43 usecase1[Add patchant]........................................")
id=1
fName="raj"
lname="    Kresh"
hasIsurance=True
billAmt="10000"
billAmt=float(billAmt)
ip="255.254.345.111"

print(id, fName,lname.lstrip(), hasIsurance,billAmt, ip[12:len(ip)]  )


print("S4.44 usecase2[student| CourseList]........................................")
stuMap={'kre':['Mat','Sci','Eng'],  'dha':['java','Python','angular']}

stuKeys=stuMap.keys()
for eachStu in stuKeys:
    print("courseTakenBy:",eachStu ,"   couses are:")
    for eachcourse in stuMap[eachStu]:
        print(eachcourse)


# list of country| add at end |  remove by index | add at middle
lstofCount=["aaa","bbb","ccc","dddd","dd2"]
lstofCount.append("eee")
#lstofCount.remove("bbb")
del(lstofCount[0])
im=int(len(lstofCount)/2)
print (im)
lstofCount.insert(im,"middle")

print (lstofCount)  #['bbb', 'ccc', 'dddd', 'eee', 'middle']



