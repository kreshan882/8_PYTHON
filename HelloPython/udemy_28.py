print("28: 251:Database Operation [CURD].................................")
#udemy_python local DB
#create table emp (id int, name varchar(100) , sal int)
#pip3 install mysql-connector-python
import mysql.connector
from mysql.connector import Error


try:
    conn=mysql.connector.connect(host="localhost",database="udemy_python",user="root",password="password")

    if conn.is_connected():
        print("connection success")
    cursor=conn.cursor()

    #***Select one by obe************************************
    cursor.execute("select * from emp")
    row=cursor.fetchone()
    while row is not None:
        print(row)
        row=cursor.fetchone()

    #****Select All****************************************
    cursor.execute("select * from emp")
    rows=cursor.fetchall()
    for row in rows:
        print(row)

    #**** Insert*******************************************   
    try:
        cursor.execute("insert into emp values (3,'Kowsik',30000)")
        conn.commit()
        print("insert success")
    except:
        conn.rollback()
        print("insert fail")

    #**** delete******************************************* 
    id=3
    strdel="delete from emp where id='%d'"
    args=(id)
    try:
        cursor.execute(strdel % args)
        conn.commit()
        print("delete success")
    except:
        conn.rollback()
        print("delete fail")

except Error as e:
    print("Error while connecting to MySQL:", e)

finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()
        print("MySQL connection is closed")


print("29: 261:PostgreSQL DB.................................")
#import psycopg2

print("30: 266:Mongo DB.................................")
# Unstructure DB ---> Collections(Json format)
# Tool : MongoDBCompress-GUI | 
print("268: Use Mongo Console...........................")
# Shell : https://www.mongodb.com/try/download/shell --> 
#        C:\PORTABLE_K\MONGO_SHELL_mongosh-1.10.6-win32-x64\bin
#        C:\PORTABLE_K\MONGO_SHELL_mongosh-1.10.6-win32-x64\bin\mongosh
"""
C:\PORTABLE_K\MONGO_SHELL_mongosh-1.10.6-win32-x64\bin\mongosh
test>
show dbs
use udemy_python ---> create Db and switch to that
db.product.insert({"name":"iphone","prize":12000})
db.product.insert({"name":"samsung","prize":10000})
show dbs
show collections
db.product.find() ---> find all
db.product.find({"name":"samsung"})
db.product.update({"name":"samsung"},{$set:{"prize":"1500"}})
db.product.remove({}) ---> remove all

pip3 install pymongo
.........
"""

# import pymongo
from pymongo import MongoClient
client=MongoClient('localhost',27017)
db=client['udemy_python']
print("db createt.....")
collection=db['product']
print("collection created...")

prosd=[
  {
    "name": "aaa",
    "prize": 12000
  },
  {
    "name": "bbb",
    "prize": 15000
  }
]

#insert
result=collection.insert_many(prosd)
print(result.inserted_ids)

#read
cursor=collection.find({"name":"aaa"})
for each_one in cursor:
    print(each_one)

#update
filter={"name": "aaa"}
count=collection.update_many(filter, {"$set": {"prize":1111} })
print("Update count:",count.modified_count)

#delete
collection.delete_many({"name": "aaa"})


print("31: 276:Debug -PyDev |PyChar.................................")

print("32: Match Cases.................................")

list1=["a","b","ccc"]
match list1:
    case["a","b"]:
        print("all list not match")
    case["a","b","ccc"]:
        print("all list matched")
    case _:
        print("not matched")


print("33:284 Virtual Environmant.................................")
# Localy install All Python libearys in Folder, instance of global install
"""
python3 -m venv C:\PORTABLE_K\PythonLibList
After activate
....PythonLibList\env\script\activate
....PythonLibList\env\script\deactivate
"""

print("34:285 Unit Testing.................................")

