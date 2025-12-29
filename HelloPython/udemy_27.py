print("239:Networking.................................")
#urllib: url&Image  | socket: clientServer | smtplib: email

import urllib.error
import urllib.request

try:
    url =urllib.request.urlopen("https://www.python.org/")
    content=url.read()
    url.close
    #print("containt:",content)
except urllib.error.HTTPError:
    print("webpagenot found")
    exit()

#------------------------------------------------------------------

import urllib.request

url = "https://www.python.org/static/community_logos/python-logo.png"
urllib.request.urlretrieve(url, "udemy_27_pythonLogoK.png")

#######################################################
#socket: clientServer 

import socket

host='localhost'
port=4000

s= socket.socket(socket.AF_INET,socket.SOCK_STREAM) #ipv4, TCP-IP
s.bind((host,port))
print("SER Server listining port:",port)
s.listen(1) # no of connection
con,addr=s.accept()
print("SER connection from:",str(addr))
con.send("thanks for connection".encode())
con.close()

#####################################################
# SMTP
#gmail->profile(manage your account) --> app password

import smtplib
from email.mime.text import MIMEText

msg =MIMEText("Hi Sir i am the email body. ThnakYoy")
msg['From']="kreshan882@gmail.com"
msg['To']="wipro@gmail.com"
msg['Subject']="Test Email"

server =smtplib.SMTP('smtp.gmeil.com',587)
server.starttls()
server.login("kreshan882@gmail.com", "xyzabc123") #app password
server.send_message(msg)
print("Main send")
server.quit()


