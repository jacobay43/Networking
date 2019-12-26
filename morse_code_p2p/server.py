# -*- coding: cp1252 -*-
#Server acts as the middle man in the peer to peer network, when one peer sends a message to another, it actually sends it to the server. The server then sends it to the other peer
import threading
import socket

class Server(threading.Thread):
    def __init__(self, connection, address, threadCount):
        global threads
        global clientMessage
        threading.Thread.__init__(self)
        self.connection = connection
        self.address = address
        self.clientMessage = "__init__"
        self.serverMessage = "__init__"
        self.threadCount = threadCount
        self.clientMessage = clientMessage
        self.otherConnected = False #used to know if there is another client connected to the server
        self.otherClient = None #the reference to the other clients connection

        #try to gain access to the other client thread through through the other index apart from threadCount
        if self.threadCount == 1:
            i = 2
            if type(threads[i] != type(None)):
                self.otherClient = threads[i]
                self.otherConnected = True
        elif self.threadCount == 2:
            i = 1
            if type(threads[i] != type(None)):
                self.otherClient = threads[i]
                self.otherConnected = True
    def run(self):
        global clientMessage
        global mySocket #call global socket so it can be closed when thread finishes executing
        if type(self.otherClient) != type(None):#notify the client that it another client has connected to the server, it should be noted that the first client to connect is the first to send a message
            self.otherClient.connection.send('Computer '+str(self.threadCount)+' connected')
        while self.clientMessage != "TERMINATE":
            if clientMessage == "TERMINATE":
                break
        if type(self.connection) != type(None):
            self.connection.close() #close all connections and the server socket if a particular client has TERMINATED the connection
        if type(self.otherClient) != type(None):
            self.otherClient.connection.close()
        if type(mySocket) != type(None):
            mySocket.close() #this is used to avoid usage error
    @staticmethod
    def toMorseCode(inputString):
        #made static so it can be accessed by ReceiverThread
        alphanumerics = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P"
                 ,"Q","R","S","T","U","V","W","X","Y","Z","1","2","3","4","5","6"
                 ,"7","8","9","0"]
        morseCodes = [".- ","-... ","-.-. ","-.. ",". ","..-. ","--. ",".... ",".. ",".--- ",
              "-.- ",".-.. ","-- ","-. ","--- ",".--. ","--.- ",".-. ","... ","- ",
              "..- ","...- ",".-- ","-..- ","-.-- ","--.. ",".---- ","..--- ","...-- ",
              "....- ","..... ","-.... ","--... ","---.. ","----. ","----- "]
        #convert all punctuation marks to spaces so they are not mistaken as morse codes
        inputString = inputString.replace(',',' ');
        inputString = inputString.replace('|',' ');
        inputString = inputString.replace('}',' ');
        inputString = inputString.replace('~',' ');
        inputString = inputString.replace('[',' ');
        inputString = inputString.replace('\\',' ');
        inputString = inputString.replace(']',' ');
        inputString = inputString.replace('^',' ');
        inputString = inputString.replace('_',' ');
        inputString = inputString.replace('\'',' ');
        inputString = inputString.replace('{',' ');
        inputString = inputString.replace('.',' ');
        inputString = inputString.replace(':',' ');
        inputString = inputString.replace('!',' ');
        inputString = inputString.replace('"',' ');
        inputString = inputString.replace('#',' ');
        inputString = inputString.replace('$',' ');
        inputString = inputString.replace('%',' ');
        inputString = inputString.replace('&',' ');
        inputString = inputString.replace('‘',' ');
        inputString = inputString.replace(':',' ');
        inputString = inputString.replace(';',' ');
        inputString = inputString.replace('>',' ');
        inputString = inputString.replace('=',' ');
        inputString = inputString.replace('<',' ');
        inputString = inputString.replace('?',' ');
        inputString = inputString.replace('@',' ');
        inputString = inputString.replace('(',' ');
        inputString = inputString.replace(',',' ');
        inputString = inputString.replace('*',' ');
        inputString = inputString.replace('+',' ');
        inputString = inputString.replace('-',' ');
        inputString = inputString.replace('.',' ');
        inputString = inputString.replace('/',' ');

        inputString = inputString.upper()
        inputString = inputString.replace(" ","   ")

        for i in range(len(alphanumerics)):
            inputString = inputString.replace(alphanumerics[i], morseCodes[i])

        return inputString    
        
class ReceiverThread(threading.Thread):
    def __init__(self, _from, _to):
        threading.Thread.__init__(self)
        self._from = _from
        self._to = _to
    def run(self):
        global clientMessage
        global shouldReceive
        global threads
        while shouldReceive:
            try:
                clientMessage = threads[self._from].connection.recv(1024)
                if clientMessage == "TERMINATE":
                    break
                else:
                    threads[self._to].connection.send(Server.toMorseCode("CLIENT "+str(self._from)+">>> "+clientMessage))
            except Exception, ex:
                if type(threads[self._from].connection) != type(None):
                    threads[self._from].connection.close()
                if type(threads[self._to].connection) != type(None):
                    threads[self._to].connection.close()
                print ex
                break
        if type(threads[self._from].connection) != type(None):
            threads[self._from].connection.close()
        if type(threads[self._to].connection) != type(None):
            threads[self._to].connection.close()
        
if __name__ == '__main__':
    HOST = "127.0.0.1"
    PORT = 5000

    clientMessage = ""
    shouldReceive = True
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.bind((HOST, PORT))
    threadCount = 0
    threads = [None, None, None] #index 0 is never used
    print "*****************Multithreaded Server*****************"
    print "What is the number of clients the server should handle? 2"
    numberOfClients = 2
    
    while threadCount < numberOfClients:
        mySocket.listen(1)
        connection, address = mySocket.accept()
        print "\nNew client added",
        threadCount += 1
        print "as Client",threadCount
        thread = Server(connection, address, threadCount)
        threads[threadCount] = thread
        thread.start()
    receiverThread1 = ReceiverThread(1,2) #a receiver thread that listens for a message from client 1 and sends it to client 2
    receiverThread2 = ReceiverThread(2,1) #a receiver thread that listens for a message from client 2 and sends it to client 1
    receiverThread1.start()
    receiverThread2.start()
    print "Server stopped listening for new clients"
