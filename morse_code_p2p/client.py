#BUG: Any peer can break the ice in the chat but the 2 peers must exchange at least one message or error arises when Quitting
import socket
from Tkinter import *
import Pmw
import easygui
import threading

class Client(Frame, threading.Thread):
    def __init__(self, mySocket):
        Frame.__init__(self)
        threading.Thread.__init__(self)
        Pmw.initialise()

        self.mySocket = mySocket
        self.master.title("Morse Code Transmitter")
        self.master.geometry("520x300")

        self.label = Label(self, text = "Message")
        self.label.grid(row = 0, column = 5)
        
        self.label1 = Label(self, text = "English")
        self.label1.grid(row = 0, column = 20)

        self.label2 = Label(self, text = "Morse Code Received")
        self.label2.grid(row = 0, column = 35)

        self.text1 = Pmw.ScrolledText(self, text_width = 20, text_height = 15, text_wrap = WORD, vscrollmode = "dynamic")
        self.text1.grid(row = 2, column = 0, columnspan = 15)

        self.text2 = Pmw.ScrolledText(self, text_width = 20, text_height = 15, text_wrap = WORD, vscrollmode = "dynamic")
        self.text2.grid(row = 2, column = 20)

        self.text3 = Pmw.ScrolledText(self, text_width = 20, text_height = 15, text_wrap = WORD, vscrollmode = "dynamic")
        self.text3.grid(row = 2, column = 35)

        self.sendButton = Button(self, text = "Send", command = self.sendMessage)
        self.sendButton.grid(row = 19, column = 5)

        self.quitButton = Button(self, text = "Quit",  command = self.closeConnection)
        self.quitButton.grid(row = 19, column = 20)

        self.grid()

        self.start()
    def run(self):
        #run method is similar to that of receiverThread in Server
        global shouldReceive
        global serverMessage
        global hasReceived
        global mySocket
        try:
            while shouldReceive:
                serverMessage = self.mySocket.recv(8192)
                hasReceived = True
                self.text3.settext(self.text3.get()+serverMessage)
                self.text2.settext(self.text2.get()+self.toEnglish(serverMessage))
            self.mySocket.close()
            mySocket.close()
        except Exception:
            print "Thread Terminated"
    def toEnglish(self, inputString):
        alphanumerics = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P"
                 ,"Q","R","S","T","U","V","W","X","Y","Z","1","2","3","4","5","6"
                 ,"7","8","9","0"]
        morseCodes = [".-","-...","-.-.","-..",".","..-.","--.","....","..",".---","-.-",".-..","--","-.","---",".--.","--.-",".-.","...","-","..-","...-",".--",
                 "-..-","-.--","--..",".----","..---","...--","....-",".....","-....","--...","---..","----.","-----"]
        if inputString.find("   ") < 0: #if single morse code without space
            inputString += "   " #append spaces to it

        tokens = inputString.split(" ") #split morse codes on each space
        result = ""
        isOneSpace = False

        for token in tokens:
            if token  == "" and isOneSpace == False:
                result += " "
                isOneSpace = True
            for i in range(len(morseCodes)):
                if morseCodes[i] == token: #for each morse code detected as a token...
                    result += alphanumerics[i] # add the corresponding alphanumeric to the result
                    isOneSpace = False #a new character has been added so a single space can be set
        return result
    def sendMessage(self):
        try:
            self.mySocket.send(self.text1.get())
            self.text2.settext(self.text2.get()+("YOU >>>"+self.text1.get()).upper())
            self.text1.settext("")
        except Exception:
            print "Cannot send because connection has been terminated"
    def closeConnection(self):
        global mySocket
        global shouldReceive
        if type(self.mySocket) != type(None):
            self.mySocket.send("TERMINATE")
        print "Connection Terminated"
        shouldReceive = False
        self.mySocket.close()
        mySocket.close()

def main(mySocket):
    Client(mySocket).mainloop()

if __name__ == '__main__':
    HOST = "127.0.0.1"
    PORT = 5000
    shouldReceive = True
    hasReceived = False
    serverMessage = ""

    #create a socket
    print "Attempting connection"
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    mySocket.connect((HOST, PORT))
    print "Connected to Server"

    main(mySocket)
    shouldReceive = False
    mySocket.close()
