import socket
import time
import threading
angle = 0.0
distance = 0.0



###this is the first hub client to recieve data from unity and convert to python output
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    retries = 5  # Number of retries
    for attempt in range(retries):
        try:
            # Attempt to connect to the Unity server
            client_socket.connect(('127.0.0.1', 12345))###localhost connection as the unity environment is running on same machine
            print("Connected to Unity server!")
            return client_socket
        except ConnectionRefusedError:
            print(f"Connection refused, retrying... ({attempt+1}/{retries})")
            time.sleep(2)
    raise Exception("Unable to connect after several retries.")

def receive_data(client_socket,test):
    global angle###create global variables that can be referenced if updated by a thread
    global distance
    try:
        while True:
            data = client_socket.recv(1024)  # Receive data from the server
            if not data:
                break
            # Decode the received data
            data_str = data.decode('utf-8')
            angle, distance = data_str.split(',')

            pass

            
    except KeyboardInterrupt:
        print("Client stopped.")





test = 1.1





local_socket = start_client()### Dedicate a thread to constantly update VR angle and distance in python
thread = threading.Thread(target = receive_data, args=(local_socket,test))
thread.start()






server_socket0 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)###create 3 server sockets to connect to each individual pi without breaking a connection with another one
server_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# local machine name over LAN, will change per-network so would need to be updated per use case
host = '10.250.16.99'




# bind each created socket to the host name and a user defined port
server_socket0.bind((host, 1234))
server_socket1.bind((host, 2345))
server_socket2.bind((host, 3456))


###server connection function so that connections can be threaded (run in parallel)
def servercon(server, client, test):
    server.listen(2)
    client, addr = server.accept()
    print("connected to", addr)
    while True:
        print(angle, distance)
        sentAng = str(angle)
        sentDist = str(distance)
        message = sentAng + ',' + sentDist
        print(message)
        client.send(str(message).encode())
        message = ''
        time.sleep(.5)

###create empty variables to be referenced by thread module
client_socket0 = None
client_socket1 =None
client_socket2 = None

###first socket thread
thread0 = threading.Thread(target = servercon, args=(server_socket0,client_socket0, test))
thread0.start()

###second socket thread
thread2 = threading.Thread(target = servercon, args=(server_socket2,client_socket2, test))
thread2.start()



### same as the function above but does not need to be threaded as it is the last remaining socket to be referenced
server_socket1.listen(2)
client_socket1, addr1 = server_socket1.accept()
print("connected to", addr1)
while True:
    print(angle, distance)
    sentAng = str(angle)
    sentDist = str(distance)
    message = sentAng + ',' + sentDist
    print(message)
    client_socket1.send(str(message).encode())
    message = ''
    time.sleep(.5)

