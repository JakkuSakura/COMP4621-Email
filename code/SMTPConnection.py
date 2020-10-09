#!/usr/bin/python3

"""
SMTPConnection.py is the core part of the server, it negotiates with the client
and responds to every request issued by the client. After the client sends the
whole message to the server, SMTPConnection creates another object called
MessageSave and puts the message body, sender address and receiver address
into it.


You need to review this code first and complete all missing sections. Replace
all '''Fill in''' with your code.
"""

import socket
import threading
import re
from MessageSave import MessageSave


# Class for spawning a new SMTP connection for the connected client.
class SMTPConnection(threading.Thread):
    BUFF = 1024
    CRLF = '\r\n'
    SENDER = False
    RECEIVER = True

    # The hostname of the local machine and remote machine
    localHost = ''
    remoteHost = ''

    # Constructor
    def __init__(self, clientsock, clientaddr):
        threading.Thread.__init__(self)

        # The socket to the client
        self.clientsock = clientsock

        # Address and port of the client
        self.clientaddr = clientaddr

        # Transform the socket into a file object for easy data operation
        self.fromClient = clientsock.makefile()

    # Function that will be executed in the thread
    def run(self):
        self.processRequest()

    def processRequest(self):
        # flag to indicate client quit the connection
        quit = False
        # flag to indicate the connection is reset
        HELOagain = False
        # flag to indicate the connection is reset
        Reset = False
        # String variable to store the client command
        requestCommand = ''
        # String variable to store the sender information
        sender = ''
        # String variable to store the receiver information
        receiver = ''

        # Get the hostname of the local machine and remote machine.
        self.localHost = socket.gethostname()
        self.remoteHost = socket.gethostbyaddr(self.clientaddr[0])[0]

        print('localHost: ', self.localHost)
        print('remoteHost: ', self.remoteHost)

        # Send the appropriate SMTP Welcome command.
        self.reply('''Fill in''')

        # Wait the client to send the HELO or EHLO command
        while not quit:
            requestCommand = self.fetch()
            # if nothing is read from fetch, quit this session
            if len(requestCommand) == 0:
                quit = True
            # Check whether HELO or EHLO is sent by client
            elif requestCommand[:4] == 'HELO' or requestCommand[:4] == '''Fill in''':
                if self.parseHELO(requestCommand):
                    break
            # Check if client want to close the connection
            elif requestCommand[:4] == '''Fill in''':
                quit = True
            # Check if the client want to reset the connection
            elif requestCommand[:4] == 'RSET':
                self.reply("250 Connection is reset")
            # If the client send the command that is not expected to see now, output an error
            elif requestCommand[:4] == 'MAIL' or requestCommand[:4] == '''Fill in''' or requestCommand[:4] == '''Fill in''':
                self.reply('''Fill in''')
            # For other unrecognized command, post the error reply here
            else:
                self.reply("500 Command unrecognized: \""+requestCommand+"\"")
            print("Stage 1: "+requestCommand)

        while not quit:
            HELOagain = False
            Reset = False
            # Wait for Mail session
            while (not quit) and (not HELOagain) and (not Reset):
                requestCommand = self.fetch()
                # if nothing is read from fetch, quit this session
                if len(requestCommand) == 0:
                    quit = True
                # If the client address MAIL command, validate it with validate()
                elif requestCommand[:4] == '''Fill in''':
                    if self.validate(requestCommand, self.SENDER):
                        sender = requestCommand[10:].strip()
                        self.reply("250 Sender "+sender+" ...OK")
                        break
                # Check whether HELO or EHLO is sent by client
                elif requestCommand[:4] == 'HELO' or requestCommand[:4] == 'EHLO':
                    if self.parseHELO(requestCommand):
                        HELOagain = True
                # Check if client want to close the connection
                elif requestCommand[:4] == '''Fill in''':
                    quit = True
                # Check if the client want to reset the connection
                elif requestCommand[:4] == '''Fill in''':
                    Reset = True
                    self.reply('''Fill in''')
                # If the client issued command in wrong order, reply it with error
                elif requestCommand[:4] == 'RCPT' or requestCommand[:4] == 'DATA':
                    self.reply("503 Bad sequence of commands")
                # For other unrecognized command, post the error reply here
                else:
                    self.reply("500 Command unrecognized: \""+requestCommand+"\"")
                print("Stage 2: "+requestCommand)
            # Wait for Receipant session
            while (not quit) and (not HELOagain) and (not Reset):
                requestCommand = self.fetch()
                # if nothing is read from fetch, quit this session
                if len(requestCommand) == 0:
                    quit = True
                # If the client send the appropriate command
                elif requestCommand[:4] == '''Fill in''':
                    if self.validate(requestCommand, self.RECEIVER):
                        receiver = requestCommand[8:].strip()
                        self.reply('''Fill in''')
                        break
                # Check whether HELO or EHLO is sent by client
                elif requestCommand[:4] == 'HELO' or requestCommand[:4] == 'EHLO':
                    if self.parseHELO(requestCommand):
                        HELOagain = True
                # Check if client want to close the connection
                elif requestCommand[:4] == 'QUIT':
                    quit = True
                # Check if the client want to reset the connection
                elif requestCommand[:4] == 'RSET':
                    Reset = True
                    self.reply("250 Connection is reset")
                # If the client issued command in wrong order, reply it with error
                elif requestCommand[:4] == 'MAIL' or requestCommand[:4] == 'DATA':
                    self.reply("503 Bad sequence of commands")
                # For other unrecognized command, post the error reply here
                else:
                    self.reply("500 Command unrecognized: \""+requestCommand+"\"")
                print("Stage 3: "+requestCommand)
            # Wait for data session
            while (not quit) and (not HELOagain) and (not Reset):
                requestCommand = self.fetch()
                # if nothing is read from fetch, quit this session
                if len(requestCommand) == 0:
                    quit = True
                # If the client start DATA command, pass the control to receiveMessage() and reply the client
                elif requestCommand[:4] == '''Fill in''':
                    self.reply('''Fill in''')
                    if self.receiveMessage(sender,receiver):
                        self.reply('''Fill in''')
                    else:
                        self.reply('''Fill in''')
                    HELOagain = True
                # Check whether HELO or EHLO is sent by client
                elif requestCommand[:4] == 'HELO' or requestCommand[:4] == 'EHLO':
                    if self.parseHELO(requestCommand):
                        HELOagain = True
                # Check if client want to close the connection
                elif requestCommand[:4] == 'QUIT':
                    quit = True
                # Check if the client want to reset the connection
                elif requestCommand[:4] == 'RSET':
                    Reset = True
                    self.reply("250 Connection is reset")
                # If the client issued command in wrong order, reply it with error
                elif requestCommand[:4] == '''Fill in''' or requestCommand[:4] == '''Fill in''':
                    self.reply("503 Bad sequence of commands")
                # For other unrecognized command, post the error reply here
                else:
                    self.reply("500 Command unrecognized: \""+requestCommand+"\"")
                print("Stage 4: "+requestCommand)

        # Send the closing connection message and then close the socket
        self.reply("221 "+self.localHost+" Service closing transmission channel")
        self.clientsock.close()

    # This method centralize the socket output operations
    def reply(self, command):
        data = command + self.CRLF
        # send reply through the socket
        self.clientsock.send(data.encode())
        print(command)

    # This method fetch each line from rawData
    def fetch(self):
        message = self.fromClient.readline()
        # If the message is less than 4 characters, display error and read again
        while len(message.strip()) < 4:
            self.reply('''Fill in''')
            message = self.fromClient.readline()
        return message.strip()

    # This method checks whether the message is HELO or EHLO
    def parseHELO(self, command):
        # differentiate EHLO and HELO
        if command[:4] == 'EHLO':
            isEHLO = True
        else:
            isEHLO = False
        # Check whether it is a valid HELO/EHLO command (with domain)
        if re.fullmatch('\\s+(\\w+\\.)*\\w+\\s*', command[4:]):
            # if it is a EHLO, display the greetings with server compatibility
            if '''Fill in''':
                self.reply("250-" + self.localHost + " greets " + self.remoteHost)
                self.reply("250 8BITMIME")
            # if it is a HELO, display the greetings only
            else:
                self.reply('''Fill in''')
            return True
        # if the HELO/EHLO is invalid, display the error message
        else:
            self.reply('''Fill in''')
            return False

    # This method checks whether the sender and receiver have valid email address or not
    def validate(self, user, isReceiver):
        ok = False
        # If we check the receiver email, the domain must be "@cs.ust.hk"
        if isReceiver:
            if re.fullmatch('^RCPT TO:\\s*<[\\w\\.]+@\\w+(\\.\\w+)*>\\s*', user):
                if re.fullmatch('^RCPT TO:\\s*<[\\w\\.]+@cs\\.ust\\.hk>\\s*', user):
                    ok = True
                else:
                    # display the error code if it doesn't fulfill the requirement
                    self.reply("550 Requested action not taken: mailbox unavailable")
            else:
                self.reply("501 Syntax error in parameters or arguments")
        # If we check the sender email, we only check whether it confirms to normal address formatting
        elif re.fullmatch('^MAIL FROM:\\s*<[\\w\\.]+@\\w+(\\.\\w+)*>\\s*', user):
            ok = True
        # display the error code if it doesn't fulfill the requirement
        else:
            self.reply("501 Syntax error in parameters or arguments")
        return ok

    # This method get the message data and pass it to another class for processing
    def receiveMessage(self, sender, receiver):
        body = ''
        # Read each line from client
        line = self.fromClient.readline().rstrip()
        while not line == '.':
            print(line)
            # Check if the beginning of line is "." or not
            if re.fullmatch('\\..*', line):
                body += line[1:]+self.CRLF
            else:
                body += line + self.CRLF
            line = self.fromClient.readline().rstrip()
        body += line[1:] + self.CRLF
        # Save the body to file by calling MessageSave class
        newMessage = MessageSave(sender, receiver, body)
        return newMessage.save()
