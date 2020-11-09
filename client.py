import socket

host = socket.gethostname()
port = 12309

client_socket = socket.socket()
client_socket.connect(("192.168.17.123", port))

msg = ""

while msg!="8":
    msg = client_socket.recv(1024).decode()
    print(msg)

client_socket.close()
