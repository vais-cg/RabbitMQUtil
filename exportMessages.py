from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QDialog,
QDialogButtonBox, QGroupBox, QHBoxLayout,
QLabel, QLineEdit, QVBoxLayout, QFileDialog, QPushButton, QPlainTextEdit, QMessageBox)

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon

from PyQt5 import QtCore

from PyQt5.QtCore import Qt, pyqtSignal

import json

from messagebox import MessageBox

__IMAGES_PATH__ = ""

class ExportMessagesDialog(QDialog):

    _fileName = QtCore.pyqtSignal(str)

    def __init__(self, images_path):
        super(ExportMessagesDialog, self).__init__()       

        __IMAGES_PATH__ = images_path

        self.messages = None

        self.frame = None

        self.resize(800, 600)

        #self.setWindowIcon(QtGui.QIcon(__IMAGES_PATH__ + '/rabbit_icon.jpg'))

        self.createFormGroupBox()

        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)  

        self.exportMessagesButtonBox = QDialogButtonBox()
        self.exportMessagesButtonBox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        
        self.exportMessagesButtonBox.button(QDialogButtonBox.Ok).setText(self.tr("Export Message(s)"))
        self.exportMessagesButtonBox.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))

        self.exportMessagesButtonBox.button(QDialogButtonBox.Ok).setIcon(QIcon(__IMAGES_PATH__ + '/export_messages.png'))
        self.exportMessagesButtonBox.button(QDialogButtonBox.Cancel).setIcon(QIcon(__IMAGES_PATH__ + '/cancel.png'))

        self.exportMessagesButtonBox.accepted.connect(self.accept)
        self.exportMessagesButtonBox.rejected.connect(self.closewin) 

        '''
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        '''

        self.btnOk = self.exportMessagesButtonBox.button(QDialogButtonBox.Ok)         
        
        self.btnOk.setEnabled(False)
        
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.exportMessagesButtonBox)
        self.setLayout(mainLayout)
        
        self.setWindowTitle("RabbitMQ - Export Messages")
        
    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("")

        layout = QVBoxLayout()      

        hbox = QHBoxLayout()        

        self.leFileName = QLineEdit()
        self.leFileName.textChanged[str].connect(lambda: self.btnOk.setEnabled(self.leFileName.text() != ""))

        hbox.addWidget(QLabel("Export File Name:"))
        hbox.addWidget(QLabel("    "))
        hbox.addWidget(self.leFileName)
        
        self.fileChooser = QPushButton("Select File ...")        
        self.fileChooser.clicked.connect(self.openFileNameDialog)
        hbox.addWidget(self.fileChooser)   

        #layout.addRow(hbox)
        layout.addLayout(hbox)

        #layout.addRow(QLabel("Display Exported Message(s):"))
        hbox1 = QHBoxLayout()        
        #layout.addRow(QLabel("Display Exported Message(s):"))
        hbox1.addWidget(QLabel("Display Exported Message(s):"))
        layout.addLayout(hbox1)

        hbox2 = QHBoxLayout()        

        self.leexportedMessages = QPlainTextEdit(self)
        self.leexportedMessages.resize(500, 500)        
        self.leexportedMessages.setStyleSheet(
        """QPlainTextEdit {background-color: #333;
                           color: #00FF00;
                           font-family: Courier;}""")
                
        
        #self.leexportedMessages.setEnabled(False)

        hbox2.addWidget(self.leexportedMessages)

        #layout.addRow(hbox2)
        layout.addLayout(hbox2)

        self.formGroupBox.setLayout(layout)           

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Select a file to export message(s)", ".","JSON Files (*.json);; All Files(*.*)", options=options)
        if fileName:
            self.leFileName.setText(fileName)

    def accept(self):        
        fileName = self.leFileName.text()
        if len(fileName) > 0:
            with open(fileName, 'w') as json_file:
                #json_file.write(self.messages)
                json_file.write(self.leexportedMessages.toPlainText())

                MessageBox.message(QMessageBox.Information, "RabbitMQ Export Message(s)", "Message(s) Exported!", "Message(s) exported to {file} sucessfully.".format(file=fileName))

        self.closewin()

    def setMessage(self, messages, frame):
        self.messages = messages
        self.leexportedMessages.setPlainText(messages)
        self.frame = frame

    def closewin(self):
        self.close()

        if self.frame is not None: 
            self.frame.close()

    def closeEvent(self, event):    
        self.close()
        
        if self.frame is not None: 
            self.frame.close()