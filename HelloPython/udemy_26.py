print("S26.217 Threads.........................................")
#1) t=Thread(target=funcName,arg)   t.start()
#2) class MyLooping(Thread)     run():   t.start()
#3) class MyLooping2   display(): t=Thread(target=myBbj.diaplay(), arg)    t.start()


import threading

print("Curr Thread:",threading.current_thread().name)
print("Main Thread:",threading.main_thread().name)

#Thread Type:1.................................................
print("type thread.......................1")
from threading import Thread

def displayNum():
    i=0
    while(i<3):
        print(threading.current_thread().name, i)
        i+=1

print(threading.current_thread().name)
t=Thread(target=displayNum)
#t.start()
    
#Thread Type:2.................................................
print("type thread.......................2")
from threading import Thread

class MyThread(Thread):
    def run(self):
        i=0
        while(i<3):
            print(threading.current_thread().name, i)
            i+=1

t=MyThread()
#t.start()

#Thread Type:3..................................................
from threading import *
from time import sleep
print("type thread.......................3")
class MyThread2:
    def displayNum(self):
        i=0
        while(i<3):
            print("Thread...3:",threading.current_thread().name, i)
            i+=1
        
obj = MyThread2()
t=Thread(target=obj.displayNum)
#t.start()
sleep(5)

t2=Thread(target=obj.displayNum)
#t2.start()

##########################################################################################
#227
#Thread Syncronization ( book seat |make payment | email ticket) 
# print action in non sequench--->start 228
#lock--->acquear --> release
print("227:Sync cal............................")
from threading import *
class BookMyBus:
    def __init__(self,avaliableSeats):
        self.avaliableSeats=avaliableSeats
        self.l=Lock() 

    def buy(self,seatRequested):
        self.l.acquire()
        print("Total seat avaliable:",self.avaliableSeats)

        if(self.avaliableSeats>=seatRequested):
            print("confirming a seat")
            print("processing the payment")
            print("printing the ticket")
            self.avaliableSeats-=seatRequested
        else:
            print("Sorry, No seats avaliable")
        self.l.release()

obj = BookMyBus(10)
t1=Thread(target=obj.buy,args=(3,))
t2=Thread(target=obj.buy,args=(4,))
t3=Thread(target=obj.buy,args=(4,))

# t1.start()
# t2.start()
# t3.start()


print("231:Produser & Consumer Thread............................")
# productur threas do the big work , and update the boolean status
# cunsumer thread monitorih each 1 second, once status change by prosucer, continue his work
from threading import *;
from time import *;

class Producer:
    def __init__(self):
        self.products = []
        self.ordersplaced = False
        
    def produce(self):
        for i in range(1,5):
            self.products.append("Product"+str(i))
            sleep(1)
            print("Item Added")
        self.ordersplaced = True

class Consumer:
    def __init__(self,prod):
        self.prod = prod
    
    def consume(self):
        while self.prod.ordersplaced == False:
            print("Waiting for the orders")
            sleep(0.2)
            
        print("Orders Shipped ",self.prod.products)
        

p = Producer()
c=Consumer(p)

t1 = Thread(target=p.produce)
t2 = Thread(target=c.consume)

# t1.start()
# t2.start()

print("234:wait() & notify() Thread simular like above............................")

from threading import *;
from time import *;

class Producer:
    def __init__(self):
        self.products = []
        self.c = Condition()
        
    def produce(self):
        self.c.acquire()
        
        for i in range(1,5):
            self.products.append("Product"+str(i))
            sleep(1)
            print("Item Added")
        self.c.notify()
        self.c.release()

class Consumer:
    def __init__(self,prod):
        self.prod = prod
    
    def consume(self):
        self.prod.c.acquire()
        self.prod.c.wait(timeout=0)
        self.prod.c.release()
        print("Orders Shipped ",self.prod.products)
        
        

p = Producer()
c=Consumer(p)

t1 = Thread(target=p.produce)
t2 = Thread(target=c.consume)

#t1.start()
#t2.start()


print("236:produse & consuming with Q............................")

import random
import time 
import queue
from threading import *

def produser(q):
    while True:
        print("producing....")
        q.put(random.randint(1,50))
        print("Prodused")
        time.sleep(3)

def consume(q):
    while True:
        print("reading Q..")
        print("Q data:",q.get())
        time.sleep(3)
        
q=queue.Queue()
t1 = Thread(target=consume, args=(q,))
t2 = Thread(target=produser, args=(q,))
#t1.start()
#t2.start()
#############################################################################################
#Queue Thpes
# q.put (400--100--500--50)
# q1 = queue.Queue()           #first in first out  400 100 500 50
# q2 = queue.LifoQueue()       #last in first out    50 500 100 400
# q3 = queue.PriorityQueue()   # sort by value       50 100 400 500

pq=queue.PriorityQueue()
pq.put(2)
pq.put(4)
pq.put(3)
pq.put(1)
while not pq.empty():
    print(pq.get(), end=' ')

pq=queue.PriorityQueue()
pq.put((2,"BBBBB"))
pq.put((4,"DDDDD"))
pq.put((3,"CCCCC"))
pq.put((1,"AAAA"))
while not pq.empty():
    print(pq.get()[1], end=' ')

#################################################################################################
#Assignment V1
from threading import *
from time import sleep
print("type thread.......................3")
class OddNumberThread:
    def displayOddNum(self):
        i=0
        while(i<10):
            if i%2!=0:
                print("OddThread:",threading.current_thread().name, i)
            i+=1

class EvenNumberThread:
    def displayEvenNum(self):
        i=0
        while(i<10):
            if i%2==0:
                print("EvenThread:",threading.current_thread().name, i)
            i+=1

obj1 = OddNumberThread()
t=Thread(target=obj1.displayOddNum)
t.start()

obj2 = EvenNumberThread()
t=Thread(target=obj2.displayEvenNum)
t.start()
############################################################
#Assignment V2
import threading
import time

current = 1
max_number = 10

def print_odd():
    global current
    while current <= max_number:
        if current % 2 == 1:
            print("Odd Function:", current)
            current += 1
        time.sleep(0.5)

def print_even():
    global current
    while current <= max_number:
        if current % 2 == 0:
            print("Event Function:",current)
            current += 1
        time.sleep(0.5)

# Create threads
t1 = threading.Thread(target=print_odd)
t2 = threading.Thread(target=print_even)

# Start threads
t1.start()
t2.start()

# Wait for both threads to finish
t1.join()
t2.join()



