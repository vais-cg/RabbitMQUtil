from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QAction, QComboBox, QDialog,
QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout,
QLabel, QLineEdit, QVBoxLayout, QFileDialog, QPushButton)

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon

from PyQt5 import QtCore

from PyQt5.QtCore import Qt, pyqtSignal

import os

import decrypt

__IMAGES_PATH__ = ""

class DecryptDialog(QDialog):   

    def __init__(self, images_path):
        super(DecryptDialog, self).__init__()         

        __IMAGES_PATH__ = images_path      

        self.passKeyFile = ""
        
        self.resize(400, 200)

        #self.setWindowIcon(QtGui.QIcon(__IMAGES_PATH__ + '/rabbit_icon.jpg'))

        self.createFormGroupBox()

        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)  
                
        self.decryptButtonBox = QDialogButtonBox()
        self.decryptButtonBox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        
        self.decryptButtonBox.button(QDialogButtonBox.Ok).setText(self.tr("Decrypt"))
        self.decryptButtonBox.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))

        self.decryptButtonBox.button(QDialogButtonBox.Ok).setIcon(QIcon(__IMAGES_PATH__ + '/decrypt.png'))
        self.decryptButtonBox.button(QDialogButtonBox.Cancel).setIcon(QIcon(__IMAGES_PATH__ + '/cancel.png'))

        self.decryptButtonBox.accepted.connect(self.decrypt_string)
        self.decryptButtonBox.rejected.connect(self.close)         

        self.btnOk = self.decryptButtonBox.button(QDialogButtonBox.Ok) 
        
        mainLayout = QVBoxLayout()
        
        mainLayout.addWidget(self.formGroupBox)
        
        mainLayout.addWidget(self.decryptButtonBox)

        self.setLayout(mainLayout)
        
        self.setWindowTitle("RabbitMQ Decrypt String")
        
    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("")
        layout = QFormLayout()       

        layout.addRow(QLabel(""), QLabel("")) # dummy row for CSS               
        
        self.stringToDecrypt = QLineEdit()        
        layout.addRow(QLabel("String to Decrypt:"), self.stringToDecrypt)

        hbox = QHBoxLayout()

        self.passKeyFile = QLineEdit()        
        hbox.addWidget(QLabel("Password Key File:"))
        hbox.addWidget(QLabel("    "))
        hbox.addWidget(self.passKeyFile)

        self.fileChooser = QPushButton("...")        
        self.fileChooser.clicked.connect(self.openFileNameDialog)
        hbox.addWidget(self.fileChooser)   

        layout.addRow(hbox)

        self.decryptedString = QLineEdit()                        
        layout.addRow(QLabel("Decrypted String:"), self.decryptedString)

        self.formGroupBox.setLayout(layout)        
    

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Choose Key File", ".","Txt Files (*.txt);; All Files(*.*)", options=options)
        if fileName:
            self.passKeyFile.setText(fileName)

    def decrypt_string(self):        

        passKeyFileName = self.passKeyFile.text()
        encPass = self.stringToDecrypt.text()       
        
        if len(passKeyFileName) != 0 and len(encPass) != 0:
            encPass = decrypt.decrypt_password(passKeyFileName, encPass.encode())
            self.decryptedString.setText(encPass)
        else:
            self.decryptedString.setText("!!! Nothing to decrypt !!!")

        #self.close()
