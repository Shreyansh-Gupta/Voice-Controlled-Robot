from socket import *
# Create a socket object
s = socket(AF_INET,SOCK_STREAM)

# Get local machine name
host = gethostname()

# Reserve a port for your service.
port = 12345
# Bind to the port
s.bind((host, port))        
print("host server , port", "Server", port)

# Now wait for client connection.
s.listen(5) 

print("Waiting for client for connection ....")

while True:
    # Establish connection with client.
   (c, addr) = s.accept()
   print ('Got connection from', addr)
   c.sendto("Connected to ",addr)
  
   a=""
   while(a!='8'):
       #print("Gaurav",end='')
       a=(input( " Enter Input : "))
       msg = a
       c.sendto(str.encode(msg),addr)
       
   # Close the connection
   c.close()
