class Student:
    def __init__(self,id,name,age):
        self.id=id
        self.name=name
        self.age=age
    
    def display(self):
        print(self.id,self.name,self.age)
