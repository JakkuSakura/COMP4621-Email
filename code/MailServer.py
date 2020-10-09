#!/usr/bin/python3

"""
MailServer.py is the frontend of the SMTP server. When a new connection is
established, MailServer creates a new object SMTPConnection for handling
this client.

To starting test your project code, run this file first to start the server
and then testing with Telnet/Email client softwares.

When working on the project, you do not need to modify this file,
but you may change the port number based on your environment configurations.
"""

from socket import *
import threading
from SMTPConnection import SMTPConnection

# The address is set to localhost, port number to 1111
HOST = '127.0.0.1'
PORT = 1111
ADDR = (HOST, PORT)
if __name__ == '__main__':
    # Establish the listening socket.
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind(ADDR)
    serversock.listen(5)

    # Process SMTP client requests in an infinite loop.
    while 1:
        # Listen for a TCP connection request.
        print('waiting for connection...')
        clientsock, addr = serversock.accept()

        # Create a new thread to process the request and start the thread.
        print('...connected from:', addr)
        connection = SMTPConnection(clientsock, addr)
        connection.start()
