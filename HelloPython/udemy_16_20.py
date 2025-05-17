print("S16.137 Object Oriented Program.................................................")
# encapsulation |inharitance| abstraction | polimorphism
#140 INIt id default Constractor function, in class

class Product:
    GlobVar="CS"
    def __init__(self):
        self.name="phone"
        self.description="blue color"
        self.prize=130

   
    def display(self):
        print("print display self method")
        print(self.name)
        print(self.description)
        print(self.prize)

p1 =Product()
print(p1.name , p1.prize)


p2 =Product()
p2.display()  #python auto pass [self] method

print(Product.GlobVar)  # print Global static variable
print(p2.GlobVar)

#...................................
class Course:
    def __init__(self,name,rating): #constractur
        self.name=name
        self.rating=rating

    def average(self):
        avg=sum(self.rating)/len(self.rating)
        print("avarage rating:",self.name,"   avg:",avg)

p3=Course("java",[1,2,3,4,5])
print(p3.name)
print(p3.rating)

p3.average()

#143 getter & Setters ..................
class Programer:
    def setName(self,n):
        self.name=n

    def getName(self):
        return self.name
    
    def setLang(self,lang):
        self.language=lang

    def getLang(self):
        return self.language
    
p5=Programer()
p5.setName("kreshan")
p5.setLang(["java","python","c++"])
print("name: ",p5.getName(),"   lang:",p5.getLang())
        
#147..... counter & staticMethod & static variable
class ObjectCounter:

    noOfObj=0
    def __init__(self):
        ObjectCounter.noOfObj+=1

    @staticmethod
    def displayCount():
        print(ObjectCounter.noOfObj)

o1=ObjectCounter()
o2=ObjectCounter()
ObjectCounter.displayCount()


#148 garbage collection
import gc
print(gc.isenabled())
gc.disable()
print(gc.isenabled())

p5=None #hardly remove the line for GC

#152 Simple program with patiend & Clinic ...............


class Pateient:
    def __init__(self,name,age):
        self.name=name
        self.age=age
        self.clinical=[]

    def addClinical(self,clinical):
        self.clinical.append(clinical)

class Clinical:
    def __init__(self,depName,depValue):
        self.depName=depName
        self.depValue=depValue


p=Pateient("kre",30)

c1=Clinical("feaver","98%")
p.addClinical(c1)

c2=Clinical("headeatach","60%")
p.addClinical(c2)

for clin in p.clinical:
    print(clin.depName,clin.depValue)



print("S17.153 Object Oriented Program.................................................")
#17 encapsulation | private variable[__age]..............................

class Student:
    def __init__(self):
        self.name="kre"
        self.__age=36 
    def getAge(self):
        return self.__age
s=Student()
print(s.name)
#print(s.age)
print(s.getAge()) #emcapsulation
print(s._Student__age) # Name Mangaling

#18 Inharitance | use the function from parent (reusabality)........
#Mathod overiding 
class IPHONE:
    def __init__(self,modal,year,prize):
        self.model=modal
        self.year=year
        self.prize=prize

class Iphone15(IPHONE):
    def __init__(self, CamPicter20Enable, modal, year, prize):
        IPHONE.__init__(self,modal, year, prize)
        self.CamPicter20Enable=CamPicter20Enable


class Iphone16(IPHONE):
    def __init__(self, CamPicter50Enable, modal, year, prize):
        IPHONE.__init__(self,modal, year, prize)
        self.CamPicter50Enable=CamPicter50Enable  

i15= Iphone15(True,"Pro",2015,"100000.00")  
print(i15.CamPicter20Enable , i15.model, i15.year, i15.prize)  


#19 Polimorpisiam | Poli:Multi , Morpisiam:Sharps........
#mather overloading === Dependency injectinon

class TradeHandeler:
    def process(self):
        print("Trade Function Started")

class CashHandeler:
    def process(self):
        print("Cash Function Started")

def callHandeler(obj):  #interface
    obj.process()

tnx1=TradeHandeler()
callHandeler(tnx1)

tnx2=CashHandeler()
callHandeler(tnx2)

#----------------------------
class TnxHandel:  #interface
    def __init__(self,engin):
        self.engin=engin

    def startEngin(self):
        self.engin.process()

class TradeHandeler:
    def process(self):
        print("Trade Function Started")

class CashHandeler:
    def process(self):
        print("Cash Function Started")

T1=TradeHandeler()
t=TnxHandel(T1)
t.startEngin()


#"+" operation is overloading
print("hello"+" kreshan")  #straing concat
print([1,2,3]+[4,5])       # list append


#20 Abstraction
print("S20.166 Abstraction.................................................")
#at lest 1 function without implementation---> need to implement class

from abc import abstractmethod,ABC
class IPHONE(ABC):
    def __init__(self,modal,year,prize):
        self.model=modal
        self.year=year
        self.prize=prize

    @abstractmethod
    def playGame(self):  # must implement in child
        pass

class Iphone15(IPHONE):
    def __init__(self, CamPicter20Enable, modal, year, prize):
        IPHONE.__init__(self,modal, year, prize)
        self.CamPicter20Enable=CamPicter20Enable

    def playGame(self):
        print("implement abstract method...")

class Iphone16(IPHONE):
    def __init__(self, CamPicter50Enable, modal, year, prize):
        IPHONE.__init__(self,modal, year, prize)
        self.CamPicter50Enable=CamPicter50Enable  

    def playGame(self):
        print("implement abstract method...")
        
i15= Iphone15(True,"Pro",2015,"100000.00")  
print(i15.CamPicter20Enable , i15.model, i15.year, i15.prize)  

#.............................................................
print("abstract Assingnment.....................")

from abc import abstractmethod,ABC
class TouchScreenLaptop(ABC):
    @abstractmethod
    def scroll(self):
        pass
    @abstractmethod
    def click(self):
        pass

class Hp(TouchScreenLaptop):
    def scroll(self):
        print("In hp override scroll")
    @abstractmethod
    def click(self):
        pass


class Dell(TouchScreenLaptop):
    def scroll(self):
        print("In DELL override scroll")
    @abstractmethod
    def click(self):
        pass


class HpNotebook(Hp):
    def __init__(self):
        print("In hpnote")

    #def scroll(self):
    #    super().scroll(self)
    #    print("In hp notebook scroll")

    def click(self):
        print("In hp notebook click")

a=HpNotebook
a.scroll(a)
a.click(a)

       

