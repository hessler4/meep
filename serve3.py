#! /usr/bin/env python
import sys
import socket
import miniapp
import string
import threading

def handle_connection(sock):
    sentinel = '\r\n\r\n'
    data = ''
    while 1:
        try:
            receivedByte = sock.recv(1)
            data += receivedByte
            if sentinel in data:
                break
        except socket.error:
            break

    try:            
        response = miniapp.buildResponse(string.split(data, '\r\n'))
        sock.sendall(response)
        sock.close()
    except socket.error:
        print 'socket failed'        



if __name__ == '__main__':
    interface, port = sys.argv[1:3]
    port = int(port)

    print 'binding', interface, port
    sock = socket.socket()
    sock.bind( (interface, port) )
    sock.listen(5)

    while 1:
        print 'waiting...'
        (client_sock, client_address) = sock.accept()
        print 'got connection', client_address
        thread = threading.Thread(target=handle_connection, args=(client_sock,))
        thread.start()