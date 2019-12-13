from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QAction, QComboBox, QDialog,
QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout,
QLabel, QLineEdit, QVBoxLayout, QFileDialog, QPushButton)

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon

from PyQt5 import QtCore

from PyQt5.QtCore import Qt, pyqtSignal

import os

import encrypt

__IMAGES_PATH__ = ""

class EncryptDialog(QDialog):   

    def __init__(self, images_path):
        super(EncryptDialog, self).__init__()               

        __IMAGES_PATH__ = images_path

        self.passKeyFile = ""
        
        self.resize(400, 200)

        #self.setWindowIcon(QtGui.QIcon(__IMAGES_PATH__ + '/rabbit_icon.jpg'))

        self.createFormGroupBox()

        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)  
                
        self.encryptButtonBox = QDialogButtonBox()
        self.encryptButtonBox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        
        self.encryptButtonBox.button(QDialogButtonBox.Ok).setText(self.tr("Encrypt"))
        self.encryptButtonBox.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))

        self.encryptButtonBox.button(QDialogButtonBox.Ok).setIcon(QIcon(__IMAGES_PATH__ + '/encrypt.png'))
        self.encryptButtonBox.button(QDialogButtonBox.Cancel).setIcon(QIcon(__IMAGES_PATH__ + '/cancel.png'))

        self.encryptButtonBox.accepted.connect(self.encrypt_string)
        self.encryptButtonBox.rejected.connect(self.close)         

        self.btnOk = self.encryptButtonBox.button(QDialogButtonBox.Ok) 
        
        mainLayout = QVBoxLayout()
        
        mainLayout.addWidget(self.formGroupBox)
        
        mainLayout.addWidget(self.encryptButtonBox)

        self.setLayout(mainLayout)
        
        self.setWindowTitle("RabbitMQ Encrypt String")
        
    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("")
        layout = QFormLayout()       

        layout.addRow(QLabel(""), QLabel("")) # dummy row for CSS
               
        self.stringToEncrypt = QLineEdit()        
        self.stringToEncrypt.setEchoMode(QLineEdit.Password)
        layout.addRow(QLabel("String to Encrypt:"), self.stringToEncrypt)

        hbox = QHBoxLayout()

        self.passKeyFile = QLineEdit()        
        hbox.addWidget(QLabel("Password Key File:"))
        hbox.addWidget(QLabel("    "))
        hbox.addWidget(self.passKeyFile)

        self.fileChooser = QPushButton("...")
        self.fileChooser.clicked.connect(self.openFileNameDialog)
        hbox.addWidget(self.fileChooser)   

        layout.addRow(hbox)

        self.encryptedString = QLineEdit()                        
        layout.addRow(QLabel("Encrypted String:"), self.encryptedString)

        self.formGroupBox.setLayout(layout)        
    

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Choose a File to Save Key", ".","Txt Files (*.txt);; All Files(*.*)", options=options)
        if fileName:
            self.passKeyFile.setText(fileName)

    def encrypt_string(self):        

        passKeyFileName = self.passKeyFile.text()
        plainPass = self.stringToEncrypt.text()       
        
        if len(passKeyFileName) != 0 and len(plainPass) != 0:
            encPass = encrypt.encrypt_password(passKeyFileName, plainPass)
            self.encryptedString.setText(encPass)
        else:
            self.encryptedString.setText("!!! Nothing to encrypt !!!")

        #self.close()
