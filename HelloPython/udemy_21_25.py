print("S21.169 Libeary management UseCase.................................................")
#polimopisam| inheritance| encapsilation

class Book:
    def __init__(self,title,author,bookId):
        self.title=title
        self.author=author
        self.bookId=bookId

    def printBook(self):
        print(f"Title:{self.title},  Author:{self.author},  Profe:{self.bookId}")

class Libeary:
    def __init__(self):
        self.books=[]

    def add_Book(self,book):
        self.books.append(book)
        print(f"book addedd to libeary:{book.title}")

    def remove_Book(self,bookId):
        removvebookObj=None
        for book in self.books:
            if book.bookId==bookId:
                removvebookObj=book
            
        if removvebookObj:
            self.books.remove(removvebookObj)
            print(f"book removed:{removvebookObj.title}")

    def display_Book(self):
        if not self.books:
            print("book not avaliable")
        else:
            for book in self.books:
                book.printBook()

class SpcialLibeart(Libeary): #inheritance
    def add_Book(self,book):
        super().add_Book(book)
        print(f"Special Adding addedd to libeary:{book.title}")

book1 =Book("DataScience","kre",1111)
book2 =Book("AI","dhar",2222)

libObj=Libeary()
libObj.add_Book(book1)
libObj.add_Book(book2)

libObj.display_Book()

#polimoposal
specialLib= SpcialLibeart()
specialLib.add_Book(book1)

print("S22.174 Exception Handeling.................................................")
#Exception ->StanderdError -> EOFError|ZeroDivitionError|IndetationError
#Exception ->Warning -> DeprecatedWarning |ImportWarning

class MyErrorResponse(Exception):
    def __init__(self, msg):
        self.msg=msg
def arraylist():
    try:
        array=[1,2,3]
        print("aaaa",array[2])
        #print("aaaa",array[5])
    except IndexError as e:
        print("indexerror:",e)
        raise MyErrorResponse("kreshan throw exception")
        #raise PasswordException("Enter Password more than eight digit")
arraylist()

try:
    f=open("udemy_21_myfile.txt","w")
    array=[1,2,3]
    print("aaaa",array[2])
   # print("aaaa",array[5])
    f.write("hi file")
except IndexError as e:
    print("indexerror:",e)
else:
    print("no exception found")
finally:
    f.close()
    print("file close success")


# customize esception 180
class TooYoungException(Exception):
    def __init__(self,msg):
        self.msg=msg

class TooOldException(Exception):
    def __init__(self, msg):
        self.msg=msg

#age=int(input("enter your age:"))
age=30
if age < 18:
    raise TooYoungException("under 18 not allow")
elif age > 50:
    raise TooOldException("more then 50 not alloewd")
else:
    print("you are eligibal")


#Log writing in sequence
import logging
logging.basicConfig(filename="udemy_21_mylogs.log",level=logging.INFO)

logging.critical("i am critical log")
logging.error("i am error log")
logging.warning("i am warning log") #default log level is warning
logging.info("i am info log")
logging.debug("i am debug log")

#assert (true|false)
#if assert false --> throw error msg
try:
    num=10
    assert num%2==0,"u have enter invalid odd number"
except AssertionError as obj:
    print(obj)

print("S23.185 Files.................................................")
#mode rread | wriite|eppend|xclusive (throw excep whan alread avaliable) default mode:4096 |8092


#fw=open("Myfile.txt","w")
#fw.write("my first file")
#fw.close

import os,sys  # special check for read file

if os.path.isfile('udemy_21_myfile.txt'):
    fr = open('udemy_21_myfile.txt','r')
    data = fr.read()
    print(data)
    fr.close()
else:
    print("file not found")
    sys.exit()

#190 pickel|unpickel (convert to Student Obj to binary file)

import pickle,udemy_21_Student
f = open("udemy_21_Student.dat","wb")
sObj=udemy_21_Student.Student(123,"kreshan",37)
pickle.dump(sObj,f)
f.close()

#read binary file....
fr=open("udemy_21_Student.dat","rb")
sObj_read=pickle.load(fr)
sObj_read.display()


print("S24.196 Regular Expressions.........................................")
#re ===> match|search|findall|split|sub
#Sequence char ==> \A \Z \d \D  \s \S \w \W \b
import re
str ="Take up One ided, One ata a time 1-12-2024  03-12-2025"
result = re.search(r'O\w\w',str)
print (result.group()) #find srtion whole word

result = re.findall(r'O\w\w',str)
print (result)  # list of data

result = re.match(r'O\w\w',str)
print (result) #Find string tart with

result = re.match(r'T\w\w',str)
print (result.group())

result = re.sub(r'One','Two',str)
print (result)

result = re.split(r'O\w\w',str) # split string when one come
print (result)

# \d+ --->one or more | * --->zero or more | ?-->o or 1 
# | {2} --> exat lenth |{1,} --> min 1 max2

result = re.findall(r'O\w{2}',str)
print (result)  # list of data

result = re.findall(r'\d{1,2}-\d{1,2}-\d{4}',str)
print (result)  # list of data


# \ . ^-start | $-end |[abc]-atart a to b| [^aba]-not a to b | (exp1|exp2) 

#202 web scrapping
import re
import urllib.request

response=urllib.request.urlopen("https://google.com")
text = response.read()
print(type(text))
string_data = text.decode('utf-8')
title=re.findall("<title>.*</title>",string_data)
print(title[0])


print("S25.208 Date & Time.........................................")
import time, datetime
STARTTIME=time.perf_counter()

timeIntk=time.time()
timek=time.ctime(timeIntk)
print(timeIntk)
print(timek)

dt= datetime.datetime.today()
print(dt)
print("TimeFormat:{}-{}-{} {}:{}:{}".format(dt.day,dt.month,dt.year,dt.hour,dt.minute,dt.second))
ENTTIME=time.perf_counter()
print("proform time:",ENTTIME-STARTTIME)




from datetime import *

dateList=[]
d1=date(2001,12,30)
d2=date(2003,12,30)
d3=date(2002,12,30)

dateList.append(d1)
dateList.append(d2)
dateList.append(d3)

dateList.sort()
print(dateList)

import datetime
#card expore validation
expire_date = datetime.date(2025, 6, 5) 
current_date = datetime.date.today()

is_valid = expire_date > current_date
print(f"Is Valid: {is_valid}")



