import os
import sys
import math
import json
import time
import PyQt5.QtWidgets as qtw
import PyQt5.QtCore as qtc
import PyQt5.QtGui as qtg
import PyQt5.QtNetwork as qtn

"""
ADD:
    +Add cancel button to stop download while progressing
    +Handling of QNetworkReply().error signal incase of download error
    +Scheme of increasing file size unit (e.g 1000 MB = 1GB, 1000 KB = 1MB, etc) in Size column of history_table
    + _ of _ (%) in QProgressBar
    Style the App
    Pause/Resume capability for downloads    
    inability to manually add entries to history_table
    ability to delete item from history_table by selecting and pressing delete which in turn recycles it to the bin on the PC
    view entire download history button and popup not just last 200
FIX:
    (fixed)if empty URL is passed, although subsequent downloads work, progressbar is permanently on busy indicator - if total is > 0, setMaximum back to 100 so indicator shows progress normally again
    (fixed)size of downloaded file QNetworkReply is always 0 - size must be gotten as early as possible(at top of on_finished slot) or it returns 0
"""
class MainWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('JDownloader')
        main_layout = qtw.QGridLayout()
        main_layout.setVerticalSpacing(6)
        self.setMinimumSize(qtc.QSize(640,240))
        self.setLayout(main_layout)
        self.url_edit = qtw.QLineEdit()   
        self.progress_bar = qtw.QProgressBar(minimum=0,maximum=100)#both should be set to 0 if size of file is not known beforehand
        self.download_btn = qtw.QPushButton('Download',clicked=self.download)
        self.cancel_btn = qtw.QPushButton('Cancel Download',clicked=self.cancel_dload)
        self.history_table = qtw.QTableWidget(columnCount=3,rowCount=200)
        self.hist_fname = 'download_history.json' #this file will load previous download history each time the app is run
        self.history_table.setHorizontalHeaderLabels(['File Path','Download Date','Size'])
        self.history_table.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.Stretch)
        if os.path.exists(self.hist_fname): #if there is a previous history, update the table with it
            self.update_table_from_json()
        else: #else create a blank file for history
            with open(self.hist_fname,'w') as _:
                pass
                      
        main_layout.addWidget(qtw.QLabel('Download URL'),1,1,1,1)
        main_layout.addWidget(self.url_edit,1,2,1,3)
        main_layout.addWidget(qtw.QLabel('Download Progress'),2,1,1,1)
        main_layout.addWidget(self.progress_bar,2,2,1,3)
        main_layout.addWidget(self.download_btn,3,1,1,2)
        main_layout.addWidget(self.cancel_btn,3,3,1,2)
        main_layout.addWidget(self.history_table,4,1,4,4)
        
        self.manager = qtn.QNetworkAccessManager(finished=self.on_finished) #the manager to handle the downloading of the requested file
        self.request = qtc.QVariant() #this variable will hold the QNetworkRequest for the download request
        self.errorOccured = False #bool var for knowing when download error occurs
        
        #Styling
        """
        app = qtw.QApplication.instance() #retrieve copy of QApplication object
        gradient = qtg.QLinearGradient(0,0,self.width(),self.height())
        gradient.setColorAt(0,qtg.QColor('navy'))
        gradient.setColorAt(0.5,qtg.QColor('darkred'))
        gradient.setColorAt(1,qtg.QColor('orange'))
        gradient_brush = qtg.QBrush(gradient)
        text_brush = qtg.QBrush(qtg.QColor('white'),qtc.Qt.Dense1Pattern)
        window_palette = app.palette()
        
        window_palette.setBrush(qtg.QPalette.Window,gradient_brush)
        window_palette.setBrush(qtg.QPalette.WindowText,text_brush)
        self.setPalette(window_palette)
        """
        self.show()
    def cancel_dload(self):
        self.manager.clearConnectionCache() #flush internal cache of network connections, essentially cancelling the current download
        self.progress_bar.reset() #reset the progress bar for the next possible download
        if hasattr(self,'reply'):
            try:
                self.reply.deleteLater() #schedule downloaded object for deletion
            except RuntimeError:
                pass
        self.download_btn.setDisabled(False) #enable download button 
        self.cancel_btn.setDisabled(True)
    def update_table_from_json(self):
        try:
            with open(self.hist_fname,'r') as fh:
                #print('Opened file',end='->')
                self.history = json.load(fh)
                #make sure number of downloads shown do not exceed the number of rows of the history table
                #if the number of downloads does exceed, show the most recent ones instead that fit into the number of rows in the table
                #e.g rowCount = 5; numDownloads = 7; show downloads 2 - 7
                if len(self.history) > self.history_table.rowCount():
                    start = int(math.fabs(len(self.history) - self.history_table.rowCount()))
                else:
                    start = 0
                rCount = 0 #rCount differs from i when updating the table with data from the history dict key list
                for i in range(start,len(self.history)): 
                    for j in range(3):
                        self.history_table.setItem(rCount,j,qtw.QTableWidgetItem(self.history[str(i)][j]))
                    rCount += 1
        except json.decoder.JSONDecodeError:
            pass
    def download(self):
        self.errorOccured = False
        self.progress_bar.reset() #used to prepare the progress bar for the next download
        self.request = qtn.QNetworkRequest(qtc.QUrl(self.url_edit.text())) #get the download request
        self.reply = self.manager.get(self.request) #begin downloading
        self.reply.downloadProgress.connect(self.update_bar) #update the progress bar as download is taking place
        self.reply.error.connect(self.on_error)
        self.download_btn.setDisabled(True) #prevent the user from mistakenly pressing the download button more than once or incase it appears download is frozen
        self.cancel_btn.setDisabled(False)
    def on_error(self,code):
        self.errorOccured = True
        qtw.QMessageBox.information(self,'Download Error',self.reply.errorString())
        try:
            self.reply.deleteLater()
        except RuntimeError:
            pass
        self.download_btn.setDisabled(False)
    def update_bar(self,current,total):
        self.progress_bar.setFormat(f'{self.format_byte(current)} of {self.format_byte(total)} (%p%) done') #format of text shown in QProgressBar
        if total <= 0: #if the download size is not known before hand, show busy indicator instead
            self.progress_bar.setMaximum(0)
        else: #else show progress of download with %
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(math.floor((current/total * 100)+.5)) #update the progress bar to indicate current download level
    def on_finished(self,reply): 
        if self.errorOccured: #finished signal is called after error signal is raised, so detect this case and exit the method if it is so
            return
        filesize = reply.size() 
        filename, accepted = qtw.QFileDialog.getSaveFileName()
        if accepted: #if the user agrees to save the downloaded file...
            with open(filename,'wb') as fh:
                fh.write(reply.readAll())
            qtw.QMessageBox.information(self,'Download Complete',f'File Saved as "{filename}"')
            
            #extract history from existing json or empty dict if json file is empty
            with open(self.hist_fname,'r') as jh:
                try:
                    self.history = json.load(jh) 
                except json.decoder.JSONDecodeError:
                    self.history = {}
            #clear contents of the json file and dump updated download history dict, 'a' mode does not work properly thus this workaround
            with open(self.hist_fname,'w') as jh:
                key = str(len(self.history)) if self.history else 0
                self.history[key] = [filename,time.ctime(time.time()),self.format_byte(filesize)] #all objects must be str as qtw.QTableWidget is compatible with str
                json.dump(self.history,jh)
            #update the history table to now show the details of the file just downloaded
            self.update_table_from_json() #better called outside the with block as for some reason when called from there it does not run
        self.download_btn.setDisabled(False)
    def format_byte(self,data): #return bytes in format B,KB,MB,GB,TB
        if data < 1000:
            return f'{data:.1f}B'
        elif 1000 < data < 1_000_000:
            return f'{data/1000:.1f}KB'
        elif 1_000_000 < data < 1_000_000_000:
            return f'{data/1_000_000:.1f}MB'
        elif 1_000_000_000 < data < 1_000_000_000_000:
            return f'{data/1_000_000_000:.1f}GB'
        else:
            return f'{data/1_000_000_000_000:.1f}TB'
if __name__ == '__main__':    
    app = qtw.QApplication(sys.argv)
    app.setStyle(qtw.QStyleFactory.create('Fusion'))
    mw = MainWindow()
    sys.exit(app.exec())
    """
    url = "https://learning-python.com/PP4E-Examples-1.4.zip"
    url2 = "https://www.renpy.org/dl/7.3.5/renpy-7.3.5-sdk.7z.exe"
    url3 = "https://media2.giphy.com/media/k61nOBRRBMxva/giphy.gif"
    url4 = "https://codeload.github.com/scottjehl/Respond/zip/master"
    url5 = "http://akino.dokisuru.com/cdn/zone1/TV_Series/Bless_The_Harts/Season_01/Bless_The_Harts_S01E01_kissTVSeries.com.mp4"
    request = qtn.QNetworkRequest(qtc.QUrl(url5))
    print(request.rawHeaderList())
    print(request.header(qtn.QNetworkRequest.ContentLengthHeader))
    """
