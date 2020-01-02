import sys
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
from http.server import HTTPServer,BaseHTTPRequestHandler

"""
NB: Received JPEGs will write to _temp.png but will not be displayed, error: QPixmap::scaled: Pixmap is a null pixmap
    The Server Address (e.g http://192.168.43.149:7777) must be known by the Client beforehand
    The roundabout method of using global variables to interact with QtWidgets is nonoptimal and should be reviewed
    alternative method of displaying info aside global vars is to define custom slots in TestHandler, make it a derived class of QtCore.QObject and have it emit the strs for visitor name, visitor purpose and path to image "_temp.png" to slots in MainWindow
"""
PORT = 8000 #port number server is on
httpd = None #global Server object for interaction with MainWindow start and stop server buttons
mw = None #make MainWindow global for interaction from TestHandler
class CustomServer(HTTPServer): #this subclass can in essence stop serve_forever(so console can be reused)
    stopped = False
    def serve_forever(self):
        while not self.stopped:
            self.handle_request()
    def force_stop(self):
        self.server_close()
        self.stopped = True
class TestHandler(BaseHTTPRequestHandler):
    def _display_request_data(self):
        print('POST request received')
        print("Content-length: {}".format(self.content_length))
        #to get the boundary separating submitted fields (appears like: .__oOOo__bondary21323)
        boundary = self.headers["Content-Type"].split(";", 1)[1].strip().replace("boundary=", "", 1)
        boundary = boundary.replace("\"","")
        comps = self.data.split(boundary.encode())
        #clean fields by boundaries
        visitor_name = (self.clean_data(comps[1])).decode('utf-8') #name (converted to str)
        purpose = (self.clean_data(comps[2])).decode('utf-8') #purpose
        image = self.clean_data(comps[3]) #image (stays in bytes format)
        with open('_temp.png','wb') as fname:
            fname.write(image)
        mw.logo = qtg.QPixmap('_temp.png')
        mw.image_label.setPixmap(mw.logo.scaled(mw.image_label.width(),mw.image_label.height(),qtc.Qt.KeepAspectRatio))
        mw.name_edit.setText(visitor_name)
        #mw.purpose_edit.clear()
        mw.purpose_edit.insertPlainText(purpose)
        #do_POST should now return response from VMS Server to Client or default to accept after an elapsed time with no response
    def clean_data(self,data):
        return data.split(b'\r\n\r\n')[-1].replace(b'\r\n--',b'') #strip of headers/metadata
    def _send_200(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    def do_POST(self, *args, **kwargs):
        self.content_length = self.headers['Content-Length']
        self.data = self.rfile.read(int(self.content_length))
        self._display_request_data()
        self._send_200()
        self.wfile.write('POST successful;'.encode('utf-8'))
def run_server(server_class=CustomServer, handler_class=TestHandler):
    global httpd
    print(f"Launching server at  http://localhost:{PORT}")
    server_address = ('', PORT)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('VMS Server')
        self.setMaximumSize(qtc.QSize(250,250))
        self.name_edit = qtw.QLineEdit(readOnly=True)
        self.purpose_edit = qtw.QTextEdit(readOnly=True)
        #purpose_edit.setTextInteraction(qtc.Qt.NoTextInteraction)
        self.image_label = qtw.QLabel('Image')
        self.image_label.sizeHint = lambda : qtc.QSize(200,200)
        self.image_label.setSizePolicy(qtw.QSizePolicy.Fixed,qtw.QSizePolicy.Fixed)
        self.logo = qtg.QPixmap('icon.png')
        self.image_label.setPixmap(self.logo.scaled(self.image_label.width(),self.image_label.height(),qtc.Qt.KeepAspectRatio))
        main_layout = qtw.QGridLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(self.name_edit,1,0,1,2)
        main_layout.addWidget(self.image_label,1,2,3,1)
        main_layout.addWidget(self.purpose_edit,2,0,2,2)
        main_layout.addWidget(qtw.QPushButton('Accept Visitor'),4,0,1,1)
        main_layout.addWidget(qtw.QPushButton('Reject Visitor'),4,1,1,1)
        main_layout.addWidget(qtw.QPushButton('Run Server',clicked=self.run),5,0,1,1)
        main_layout.addWidget(qtw.QPushButton('Stop Server',clicked=self.stop_server),5,1,1,1) #stop the server
        self.show()
    def stop_server(self):
        print('Stopping Server at {}'.format(PORT))
        httpd.force_stop()
    def run(self):
        import threading
        self.t = threading.Thread(name='Server Thread',target=run_server)
        self.t.start()
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    app.setStyle(qtw.QStyleFactory.create('Fusion'))
    mw = MainWindow()
    import client #multiple windows can be running concurrently from a single QApplication instance and they are independent of each other(one's closing does not affect the other)
    mw2 = client.MainWindow()
    sys.exit(app.exec())
