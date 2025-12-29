import socket

s= socket.socket()
s.connect(("localhost",4000))
msg=s.recv(1024) # msg byte lenth

while msg:
    print("CLI Revived:",msg.decode())
    msg=s.recv(1024)

s.close()