import sys
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtNetwork as qtn

#Demerit of this method is that the the Server Address (e.g http://192.168.43.149:7777) must be known beforehand
class Poster(qtc.QObject):
    replyReceived = qtc.pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self.nam = qtn.QNetworkAccessManager()
        self.nam.finished.connect(self.on_reply)
    def on_reply(self,reply):
        reply_bytes = reply.readAll()
        try:
            reply_string = bytes(reply_bytes).decode('utf-8')
        except UnicodeDecodeError:
            reply_string = "This is an Image"
        self.replyReceived.emit(reply_string)
    def make_request(self,url,data,filename):
        self.request = qtn.QNetworkRequest(url)
        self.multipart = qtn.QHttpMultiPart(qtn.QHttpMultiPart.FormDataType)
        for key, value in (data or {}).items():
            http_part = qtn.QHttpPart()
            http_part.setHeader(qtn.QNetworkRequest.ContentDispositionHeader,f'form-data; name="{key}"')
            http_part.setBody(value.encode('utf-8'))
            self.multipart.append(http_part)
        if filename:
            file_part = qtn.QHttpPart()
            file_part.setHeader(qtn.QNetworkRequest.ContentDispositionHeader,f'form-data; name="attachment"; filename="{filename}"') #file to upload/post/submit
            filedata = open(filename,'rb').read()
            file_part.setBody(filedata)
            self.multipart.append(file_part)
        self.nam.post(self.request,self.multipart)
class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('VMS Client')
        self.url_edit = qtw.QLineEdit('http://localhost:8000')
        self.name_edit = qtw.QLineEdit('Opegbemi Ayodele')
        self.purpose_edit = qtw.QTextEdit('Congratulatory Visit notice')
        self.image_edit = qtw.QLineEdit('icon.png')
        image_btn = qtw.QPushButton('Open from disk',clicked=self.open_image)
        submit_btn = qtw.QPushButton('Submit to Server',clicked=self.submit)
        main_layout = qtw.QGridLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(qtw.QLabel('Name of Visitor'),1,0,1,1)
        main_layout.addWidget(self.name_edit,1,1,1,2)
        main_layout.addWidget(qtw.QLabel('Purpose of Visit'),2,0,1,1)
        main_layout.addWidget(self.purpose_edit,2,1,1,2)
        main_layout.addWidget(qtw.QLabel('Image Path'),3,0,1,1)
        main_layout.addWidget(self.image_edit,3,1,1,1)
        main_layout.addWidget(image_btn,3,2,1,1)
        main_layout.addWidget(qtw.QLabel('Server Address'),4,0,1,1)
        main_layout.addWidget(self.url_edit,4,1,1,2)
        main_layout.addWidget(submit_btn,5,1,1,2)
        self.poster = Poster()
        self.poster.replyReceived.connect(lambda x: qtw.QMessageBox.information(self,'Reply from Server',x))
        self.show()
    def open_image(self):
        imgname, _ = qtw.QFileDialog.getOpenFileName(
                self,
                'Select an image to open...',
                qtc.QDir.currentPath(),
                'PNG Files (*.png) ;;JPG Files (*.jpg)',
                'PNG Files (*.png)',
                qtw.QFileDialog.DontResolveSymlinks)
        if imgname:
            self.image_edit.setText(imgname)
    def submit(self):
        url = qtc.QUrl(self.url_edit.text())
        filename = self.image_edit.text()
        if not filename:
            filename = None
        data = {}
        data['name'] = self.name_edit.text()
        data['purpose'] = self.purpose_edit.toPlainText()
        self.poster.make_request(url,data,filename)      
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    app.setStyle(qtw.QStyleFactory.create('Fusion'))
    mw = MainWindow()
    sys.exit(app.exec())
