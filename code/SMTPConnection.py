#!/usr/bin/python3

'''
SMTPConnection.py is the core part of the server, it negotiates with the client
and responds to every request issued by the client. After the client sends the
whole message to the server, SMTPConnection creates another object called
MessageSave and puts the message body, sender address and receiver address
into it.


You need to review this code first and complete all missing sections. Replace
all \'\'\'Fill in\'\'\' with your code.
'''

import socket
import threading
import re
from MessageSave import MessageSave

RE_DOMAIN = r'(localhost|([\w\d_]+\.)+\w+)'
print(RE_DOMAIN)
RE_DOMAINS = rf'\s*({RE_DOMAIN}|\[{RE_DOMAIN}(, *{RE_DOMAIN})*])\s*?'
print(RE_DOMAINS)
RE_EMAIL = rf'(([\w\d_]+\.)*\w+@{RE_DOMAIN})'
print(RE_EMAIL)
RE_EMAILS = rf'\s*({RE_EMAIL}|\<{RE_EMAIL}(, *{RE_EMAIL})*>)\s*?'

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
        # flag to indicate client quit the connection
        self.quit = False
        # flag to indicate the connection is reset
        self.HELOagain = False
        # flag to indicate the connection is reset
        self.Reset = False

        # String variable to store the sender information
        self.sender = ''
        # String variable to store the receiver information
        self.receiver = ''

    # Function that will be executed in the thread
    def run(self):
        self.processRequest()

    def processRequest(self):

        # Get the hostname of the local machine and remote machine.
        self.localHost = socket.gethostname()
        self.remoteHost = socket.gethostbyaddr(self.clientaddr[0])[0]

        print('localHost: ', self.localHost)
        print('remoteHost: ', self.remoteHost)

        # Send the appropriate SMTP Welcome command.
        self.reply('220 localhost email system')

        # Wait the client to send the HELO or EHLO command
        while not self.quit:
            requestCommand = self.fetch_command()
            if not requestCommand:
                break
            op_code = requestCommand[:4].upper()
            # Check whether HELO or EHLO is sent by client
            if op_code == 'HELO' or op_code == 'EHLO':
                if self.parseHELO(requestCommand):
                    break
            # Check if client want to close the connection
            elif op_code == 'QUIT':
                self.quit = True
                break
            # Check if the client want to reset the connection
            elif op_code == 'RSET':
                self.reply('250 Connection is reset')
            # If the client send the command that is not expected to see now, output an error
            elif op_code == 'MAIL' or op_code == 'DATA' or op_code == 'RCPT':
                self.reply('503 Bad sequence of commands')
            # For other unrecognized command, post the error reply here
            else:
                self.reply('500 Command unrecognized: \'' + requestCommand + '\'')
            print('Stage 1: ' + requestCommand)

        while not self.quit:
            HELOagain = False
            Reset = False
            # Wait for Mail session
            while (not self.quit) and (not HELOagain) and (not Reset):
                requestCommand = self.fetch_command()
                if not requestCommand:
                    break

                op_code = requestCommand[:4].upper()
                # If the client address MAIL command, validate it with validate()
                if op_code == 'MAIL':
                    if self.validate(requestCommand, self.SENDER):
                        self.sender = requestCommand[10:].strip()
                        self.reply('250 Sender ' + self.sender + ' ...OK')
                        break
                # Check whether HELO or EHLO is sent by client
                elif op_code == 'HELO' or op_code == 'EHLO':
                    if self.parseHELO(requestCommand):
                        HELOagain = True
                # Check if client want to close the connection
                elif op_code == 'QUIT':
                    self.quit = True
                # Check if the client want to reset the connection
                elif op_code == 'RSET':
                    Reset = True
                    self.reply('250 Connection is reset')
                # If the client issued command in wrong order, reply it with error
                elif op_code == 'RCPT' or op_code == 'DATA':
                    self.reply('503 Bad sequence of commands')
                # For other unrecognized command, post the error reply here
                else:
                    self.reply('500 Command unrecognized: \'' + requestCommand + '\'')
                print('Stage 2: ' + requestCommand)

            # Wait for Receipant session
            while (not self.quit) and (not HELOagain) and (not Reset):

                requestCommand = self.fetch_command()
                if not requestCommand:
                    break

                op_code = requestCommand[:4].upper()
                # If the client send the appropriate command
                if op_code == 'RCPT':
                    if self.validate(requestCommand, self.RECEIVER):
                        self.receiver = requestCommand[8:].strip()
                        self.reply('250 Receiver ' + self.receiver + " ...OK")
                        break
                # Check whether HELO or EHLO is sent by client
                elif op_code == 'HELO' or op_code == 'EHLO':
                    if self.parseHELO(requestCommand):
                        HELOagain = True
                # Check if client want to close the connection
                elif op_code == 'QUIT':
                    self.quit = True
                # Check if the client want to reset the connection
                elif op_code == 'RSET':
                    Reset = True
                    self.reply('250 Connection is reset')
                # If the client issued command in wrong order, reply it with error
                elif op_code == 'MAIL' or op_code == 'DATA':
                    self.reply('503 Bad sequence of commands')
                # For other unrecognized command, post the error reply here
                else:
                    self.reply('500 Command unrecognized: \'' + requestCommand + '\'')
                print('Stage 3: ' + requestCommand)

            # Wait for data session
            while (not self.quit) and (not HELOagain) and (not Reset):

                requestCommand = self.fetch_command()
                if not requestCommand:
                    break

                op_code = requestCommand[:4].upper()
                # If the client start DATA command, pass the control to receiveMessage() and reply the client
                if op_code == 'DATA':
                    self.reply('354 Enter mail, end with "." on a line by itself')
                    if self.receive_message(self.sender, self.receiver):
                        self.reply('250 DATA Email saved ...OK')
                    else:
                        self.reply('501 Syntax error in parameters or arguments')
                    HELOagain = True
                # Check whether HELO or EHLO is sent by client
                elif op_code == 'HELO' or op_code == 'EHLO':
                    if self.parseHELO(requestCommand):
                        HELOagain = True
                # Check if client want to close the connection
                elif op_code == 'QUIT':
                    self.quit = True
                # Check if the client want to reset the connection
                elif op_code == 'RSET':
                    Reset = True
                    self.reply('250 Connection is reset')
                # If the client issued command in wrong order, reply it with error
                elif op_code == 'MAIL' or op_code == 'RCPT':
                    self.reply('503 Bad sequence of commands')
                # For other unrecognized command, post the error reply here
                else:
                    self.reply('500 Command unrecognized: \'' + requestCommand + '\'')
                print('Stage 4: ' + requestCommand)

        # Send the closing connection message and then close the socket
        self.reply('221 ' + self.localHost + ' Service closing transmission channel')
        self.clientsock.close()

    # This method centralize the socket output operations
    def reply(self, command):
        print('<', command)
        data = command + self.CRLF
        # send reply through the socket
        self.clientsock.send(data.encode())

    # This method fetch each line from rawData
    def fetch_command(self):
        message = self.readline(True)
        # If the message is less than 4 characters, display error and read again
        while message and len(message.strip()) < 4:
            self.reply('501 Command too short')
            message = self.fromClient.readline()
        if not message:
            return None

        return message.strip()

    def readline(self, validate):
        message = self.fromClient.readline().rstrip()
        print('>', message)
        if validate:
            if message == '':
                self.quit = True
                return None
        return message

    # This method checks whether the message is HELO or EHLO
    def parseHELO(self, command):
        # differentiate EHLO and HELO
        self.isEHLO = command[:4] == 'EHLO'
        # Check whether it is a valid HELO/EHLO command (with domain)
        if re.fullmatch(RE_DOMAINS, command[4:]):
            # if it is a EHLO, display the greetings with server compatibility
            if command[:4].upper() == 'EHLO':
                self.reply('250-' + self.localHost + ' greets ' + self.remoteHost)
                self.reply('250 8BITMIME')
            # if it is a HELO, display the greetings only
            else:
                self.reply('250 OK')
            return True
        # if the HELO/EHLO is invalid, display the error message
        else:
            self.reply('501 Syntax error in parameters or arguments')
            return False

    # This method checks whether the sender and receiver have valid email address or not
    def validate(self, user, is_receiver):
        user = user[:4].upper() + user[4:]
        # If we check the receiver email, the domain must be '@cs.ust.hk'
        if is_receiver:
            print("Testing receiver")
            if re.fullmatch(f'RCPT TO:{RE_EMAILS}', user):
                if re.fullmatch(r'RCPT TO:\s*<([\w\d_]+\.)*\w+@cs\.ust\.hk>', user):
                    return True
                else:
                    # display the error code if it doesn't fulfill the requirement
                    self.reply('550 Requested action not taken: mailbox unavailable')
            else:
                self.reply('501 Syntax error in parameters or arguments')

        # If we check the sender email, we only check whether it confirms to normal address formatting
        else:
            print("Testing sender")
            if re.fullmatch(f'MAIL FROM:{RE_EMAILS}', user):
                return True

            self.reply('501 Syntax error in parameters or arguments')
        return False

    # This method get the message data and pass it to another class for processing
    def receive_message(self, sender, receiver):
        body = ''
        # Read each line from client
        line = self.readline(False)
        while line != '.':
            # Check if the beginning of line is '.' or not
            if re.fullmatch('\\..*', line):
                body += line[1:] + self.CRLF
            else:
                body += line + self.CRLF
            line = self.readline(False)

        # Save the body to file by calling MessageSave class
        new_message = MessageSave(sender, receiver, body)
        return new_message.save
