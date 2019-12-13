import sys

import os

import encrypt

#from configparser import ConfigParser

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QAction, QFormLayout, QHBoxLayout, QPushButton,
QVBoxLayout, QMainWindow, QWidget, QLineEdit, QLabel, QFileDialog, QGroupBox,  
QComboBox, QStatusBar, QMessageBox)

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize, pyqtSignal

from messagebox import MessageBox

__IMAGES_PATH__ = "./resources/images"

class ConnectMenu(QtWidgets.QMainWindow):    
	
    _webUrl = QtCore.pyqtSignal(str)
    _commandUrl = QtCore.pyqtSignal(str)
    _userId = QtCore.pyqtSignal(str)
    _password = QtCore.pyqtSignal(str, str)
    _vhost = QtCore.pyqtSignal(str)
    _certName = QtCore.pyqtSignal(str)
    _certPass = QtCore.pyqtSignal(str)

    _cancelled = QtCore.pyqtSignal(bool)

    def __init__(self, parser, resources_path):
        
        super(ConnectMenu, self).__init__()

        self.filePath = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")

        #__IMAGES_PATH__ = resources_path + '/images'
		
        self.inifile = os.environ['RMQ_INI_FILE']

        self.setWindowTitle("RabbitMQ Utility - Connection")    # Set the window title

        #self.setWindowIcon(QtGui.QIcon(__IMAGES_PATH__ + '/rabbit_icon.jpg'))

        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)  
        #------------------------------
        #self.app = app       

        self.frame = None

        self.passKeyFile = ""

        self.parser = parser
        
        #------------------------------ 
        self.qapp = QApplication([])
        #V = self.qapp.desktop().screenGeometry()
        #h = V.height() - 800 
        #w = V.width() - 1100

        h = 300
        w = 800

        self.resize(w, h)
        
        self.widget = QWidget()

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
         # Create Connect
        self.connectAction = QAction(QIcon(__IMAGES_PATH__ + '/ok.png'), '&Proceed', self)        
        self.connectAction.setShortcut('SHIFT+O')
        self.connectAction.setStatusTip('Proceed')
        #self.connectAction.setEnabled(False)
        self.connectAction.triggered.connect(self.accept)      

        # Create cancel action
        self.exitAction = QAction(QIcon(__IMAGES_PATH__ + '/cancel_big.png'), '&Cancel', self)        
        self.exitAction.setShortcut('ALT+F4')
        self.exitAction.setStatusTip('Cancel')
        self.exitAction.triggered.connect(self.closewin)

        # Create Add Setting
        self.addSettingAction = QAction(QIcon(__IMAGES_PATH__ + '/add_setting.png'), '&Add Setting', self)        
        self.addSettingAction.setShortcut('SHIFT+A')
        self.addSettingAction.setStatusTip('Add Setting')
        self.addSettingAction.triggered.connect(self.addsetting)
        
        # Create Delete Setting
        self.delSettingAction = QAction(QIcon(__IMAGES_PATH__ + '/delete_setting.png'), '&Delete Setting', self)        
        self.delSettingAction.setShortcut('SHIFT+D')
        self.delSettingAction.setStatusTip('Delete Setting')
        self.delSettingAction.triggered.connect(self.deletesetting)

        # Create Update Setting
        self.updSettingAction = QAction(QIcon(__IMAGES_PATH__ + '/update_setting.png'), '&Update Setting', self)        
        self.updSettingAction.setShortcut('SHIFT+U')
        self.updSettingAction.setStatusTip('Update Setting')
        self.updSettingAction.triggered.connect(self.editsetting)
        
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.connectAction)      
        fileMenu.addAction(self.addSettingAction)
        fileMenu.addAction(self.delSettingAction)
        fileMenu.addAction(self.updSettingAction)
        fileMenu.addAction(self.exitAction)

        # ----------------- Tool Bar ------------------------------
        self.toolbar = self.addToolBar('')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)

        #self.toolbar.setIconSize(QSize(50,50))
        #self.toolbar.setGeometry(100, 100, 400, 400)

        #------------ Connect -------------
        self.loginButton = QAction(QIcon(__IMAGES_PATH__ + '/ok.png'), '&Proceed', self)
        #self.loginButton.setIconText('Proceed')
        self.loginButton.setStatusTip("Select a server and click proceed")
        self.loginButton.triggered.connect(self.accept)
        #self.loginButton.setEnabled(False)
        self.toolbar.addAction(self.loginButton)       

        #------------ Exit -------------
        self.exitButton = QAction(QIcon(__IMAGES_PATH__ + '/cancel_big.png'), '&Cancel', self)
        self.exitButton.triggered.connect(self.closewin)        
        self.exitButton.setStatusTip("Click to close this window.")
        self.toolbar.addAction(self.exitButton)   

        self.toolbar.addSeparator()

        #------------ Add Setting -------------
        self.addSettingButton = QAction(QIcon(__IMAGES_PATH__ + '/add_setting.png'), '&Add Setting', self)
        self.addSettingButton.triggered.connect(self.addsetting)
        self.addSettingButton.setStatusTip("Click to add new server setting and press Save.")
        self.toolbar.addAction(self.addSettingButton)     

        #------------ Delete Setting -------------
        self.delSettingButton = QAction(QIcon(__IMAGES_PATH__ + '/delete_setting.png'), '&Delete Setting', self)
        self.delSettingButton.triggered.connect(self.deletesetting)
        self.delSettingButton.setStatusTip("Click to delete server setting.")
        self.toolbar.addAction(self.delSettingButton)  

        #------------ Update Setting -------------
        self.updSettingButton = QAction(QIcon(__IMAGES_PATH__ + '/update_setting.png'), '&Update Setting', self)
        self.updSettingButton.triggered.connect(self.editsetting)
        self.updSettingButton.setStatusTip("Click to update server setting.")
        self.toolbar.addAction(self.updSettingButton)      

        self.toggle(False)

        self.createFormGroupBox()

        vBox = QVBoxLayout()       

        vBox.addWidget(self.formGroupBox)            

        self.widget.setLayout(vBox)
        
        self.setCentralWidget(self.widget)      

    def createFormGroupBox(self, mode=None):
        self.formGroupBox = QGroupBox("")
        layout = QFormLayout()
        
        layout.addRow(QLabel(""), QLabel("")) # dummy row for CSS

        self.leServer = QComboBox()       
        self.leServer.currentIndexChanged.connect(self.selectionchange)        
        
        self.leAddServer = QLineEdit()
                
        self.leAddServer.textEdited.connect(self.updatewhost)
        if mode is None:
            layout.addRow(QLabel("Server:                  "), self.leServer)
        else:    
            layout.addRow(QLabel("Server:                  "), self.leAddServer)

        self.leUrl = QLineEdit()
        hlay1 = QHBoxLayout()
        hlay1.addWidget(self.leUrl)

        hlay2 = QHBoxLayout()
        self.wprotocolCombo = QComboBox()
        self.wprotocolCombo.addItem("https")
        self.wprotocolCombo.addItem("http")
        self.wprotocolCombo.currentTextChanged.connect(self.onWebProtocolTextChanged)
        self.whost = QLineEdit()
        self.whost.setEnabled(False)
        self.wport = QLineEdit()
        self.wport.setFixedWidth(50)
        self.wbaseurl = QLineEdit()
        self.wbaseurl.setFixedWidth(100)

        hlay2.addWidget(self.wprotocolCombo)
        hlay2.addWidget(self.whost)
        hlay2.addWidget(self.wport)
        hlay2.addWidget(self.wbaseurl)    
        
        if mode is None:
            layout.addRow(QLabel("Web Url:                 "), hlay1)            
        else:    
            layout.addRow(QLabel("Web Url:                 "), hlay2)
        #layout.addRow(QLabel("Web Url:"), self.leUrl)

        self.le1Url = QLineEdit()
        hlay3 = QHBoxLayout()
        hlay3.addWidget(self.le1Url)

        hlay4 = QHBoxLayout()
        self.amqpCombo = QComboBox()
        self.amqpCombo.addItem("amqps")
        self.amqpCombo.addItem("amqp")
        self.amqpCombo.currentTextChanged.connect(self.onAmqpProtocolTextChanged)
        self.amqphost = QLineEdit()
        self.amqpport = QLineEdit()
        self.amqpport.setFixedWidth(150)

        hlay4.addWidget(self.amqpCombo)
        hlay4.addWidget(self.amqphost)
        hlay4.addWidget(self.amqpport)
        
        if mode is None:
            layout.addRow(QLabel("Amqp Url:                "), hlay3)
        else:    
            layout.addRow(QLabel("Amqp Url:                "), hlay4)
        #layout.addRow(QLabel("AMQP Url:"), self.le1Url)

        self.leUserId = QLineEdit()
        layout.addRow(QLabel("User Id:                 "), self.leUserId)
      
        self.lePassword = QLineEdit()        
        self.lePassword.setEchoMode(QLineEdit.Password)
        layout.addRow(QLabel("Password:                "), self.lePassword)

        hboxpass = QHBoxLayout()
        
        self.lePassKey = QLineEdit()
        hboxpass.addWidget(self.lePassKey)

        self.fileChooserpk = QPushButton("...")
        self.fileChooserpk.setEnabled(False)
        self.fileChooserpk.clicked.connect(lambda: self.openFileNameDialog(self.lePassKey, "passkey"))
        hboxpass.addWidget(self.fileChooserpk)   

        layout.addRow(QLabel("PassKey File:"), hboxpass)

        self.leVhost = QLineEdit()
        layout.addRow(QLabel("Vhost:                   "), self.leVhost)         
        hbox = QHBoxLayout()
        
        self.leCertificateName = QLineEdit()
        self.leCertificateName.setEnabled(False)
        hbox.addWidget(QLabel("Certificate Name:          "))                               
        hbox.addWidget(self.leCertificateName)

        self.fileChooser = QPushButton("...")
        self.fileChooser.setEnabled(False)
        self.fileChooser.clicked.connect(lambda: self.openFileNameDialog(self.leCertificateName, "certname"))
        hbox.addWidget(self.fileChooser)   

        layout.addRow(hbox)

        self.leCertificatePassword = QLineEdit()        
        self.leCertificatePassword.setEchoMode(QLineEdit.Password)
        self.leCertificatePassword.setEnabled(False)
        layout.addRow(QLabel("Certificate Password:    "), self.leCertificatePassword)                              
        hboxcpass = QHBoxLayout()
        
        self.leCertificatePassKey = QLineEdit()
        self.leCertificatePassKey.setEnabled(False)
        hboxcpass.addWidget(QLabel("Certificate PassKey File:"))
        hboxcpass.addWidget(self.leCertificatePassKey)

        self.fileChoosercpk = QPushButton("...")
        self.fileChoosercpk.setEnabled(False)
        self.fileChoosercpk.clicked.connect(lambda: self.openFileNameDialog(self.leCertificatePassKey, "certpasskey"))
        hboxcpass.addWidget(self.fileChoosercpk)   

        layout.addRow(hboxcpass)

        self.editButton = QPushButton("Save Setting")
        self.editButton.setObjectName('edit_setting')
        self.editButton.setIcon(QIcon(__IMAGES_PATH__ + '/update_setting.png'))
        self.editButton.setIconSize(QSize(25,25))
        self.editButton.clicked.connect(self.buttonClicked)

        self.addButton = QPushButton("Save Setting")
        self.addButton.setObjectName('add_setting')
        self.addButton.setIcon(QIcon(__IMAGES_PATH__ + '/add_setting.png'))
        self.addButton.setIconSize(QSize(25,25))
        self.addButton.clicked.connect(self.buttonClicked)

        self.cxlButton = QPushButton("Cancel")
        self.cxlButton.setObjectName('cancel_setting')
        self.cxlButton.setIcon(QIcon(__IMAGES_PATH__ + '/cancel.png'))
        self.cxlButton.setIconSize(QSize(25,25))
        self.cxlButton.clicked.connect(self.buttonClicked)

        hbox5 = QHBoxLayout()
        hbox5.addWidget(QLabel(""))
        hbox5.addWidget(QLabel(""))
        hbox5.addWidget(QLabel(""))
        
        if mode is not None:
            hbox5.addWidget(self.addButton)
        else:
            hbox5.addWidget(self.editButton)

        hbox5.addWidget(self.cxlButton)
        
        if mode is not None:
            layout.addRow(hbox5)

        self.findChangedWidget()

        self.formGroupBox.setLayout(layout)  

        if mode is None:
            self.populate()

    def buttonClicked(self):
        button = self.sender()
        #print(button.objectName())
        
        if not button: return  

        buttonObjectName = button.objectName()
        
        if buttonObjectName == "add_setting":
            
            section_name = self.leAddServer.text()
            
            self.parser.add_section(section_name)
            
            self.parser.set(section_name, 'protocol', self.wprotocolCombo.currentText().strip())
            self.parser.set(section_name, 'console.url', self.whost.text().strip())
            self.parser.set(section_name, 'console.port', self.wport.text().strip())
            self.parser.set(section_name, 'console.baseurl', self.wbaseurl.text().strip())

            self.parser.set(section_name, 'amqp.protocol', self.amqpCombo.currentText().strip())
            self.parser.set(section_name, 'amqp.url', self.amqphost.text().strip())
            self.parser.set(section_name, 'amqp.port', self.amqpport.text().strip())

            self.parser.set(section_name, 'username', self.leUserId.text().strip())

            passKeyFile = self.lePassKey.text().strip() 
            self.parser.set(section_name, 'passkey.file', passKeyFile)
            
            passwd = self.lePassword.text()
            encPass = ""
            if len(passKeyFile) != 0 and len(passwd) != 0:
                encPass = encrypt.encrypt_password(passKeyFile, passwd)
            self.parser.set(section_name, 'password', encPass)

            self.parser.set(section_name, 'vhost', self.leVhost.text().strip())
            self.parser.set(section_name, 'certificateName', self.leCertificateName.text().strip())
            
            certPasskeyFile = self.leCertificatePassKey.text().strip()
            self.parser.set(section_name, 'passkeycert.file', certPasskeyFile)

            certpasswd = self.leCertificatePassword.text()
            encCertPass = ""
            if len(certPasskeyFile) != 0 and len(certpasswd) != 0:
                encCertPass = encrypt.encrypt_password(certPasskeyFile, certpasswd)
            self.parser.set(section_name, 'certificatePassword', encCertPass)
            
            with open(self.inifile, 'w') as configfile:
                self.parser.write(configfile)

            #self.refresh() 

            MessageBox.message(QMessageBox.Information, "RabbitMQ Queue", "Configuration entry added!", \
                                   "Server: {section} added to File: {file} sucessfully.".format(section=section_name, file=self.inifile))  

            self.resetWidget()
        elif buttonObjectName == "edit_setting":
            pass
        elif buttonObjectName == "cancel_setting":
            self.resetWidget()

    def resetWidget(self):
        self.createFormGroupBox()

        self.leServer.setEditable(False)

        self.widgetback = QWidget()
        vBox = QVBoxLayout()       
        vBox.addWidget(self.formGroupBox)            
        self.widgetback.setLayout(vBox)
        self.setCentralWidget(self.widgetback)   

    def onWebProtocolTextChanged(self, text):
        if text == "https":
            self.amqpCombo.setCurrentIndex(0)
            self.leCertificateName.setEnabled(True)
            self.leCertificatePassword.setEnabled(True)
            self.leCertificatePassKey.setEnabled(True)
            self.fileChooser.setEnabled(True)
            self.fileChooserpk.setEnabled(True)
            self.fileChoosercpk.setEnabled(True)
        else:    
            self.amqpCombo.setCurrentIndex(1)
            self.leCertificateName.setText('')
            self.leCertificatePassword.setText('')
            self.leCertificatePassKey.setText('')
            self.leCertificateName.setEnabled(False)
            self.leCertificatePassword.setEnabled(False)
            self.leCertificatePassKey.setEnabled(False)
            self.fileChooser.setEnabled(False)
            #self.fileChooserpk.setEnabled(False)
            self.fileChoosercpk.setEnabled(False)

    def onAmqpProtocolTextChanged(self, text):
        if text == "amqps":
            self.wprotocolCombo.setCurrentIndex(0)
        else:    
            self.wprotocolCombo.setCurrentIndex(1)

    def findChangedWidget(self):
        self.webUrlModified = False
        self.amqpUrlModified = False
        self.userIdModified = False
        self.passwordModified = False
        self.vhostModified = False
        self.certNameModified = False
        self.certPassModified = False
        self.passkeyCertFileModified = False
        self.passkeyFileModified = False

        self.leUrl.textChanged.connect(self.httpUrlModified)
        self.le1Url.textEdited.connect(self.cmdUrlModified)
        self.leUserId.textEdited.connect(self.userModified)
        self.lePassword.textEdited.connect(self.passcodeModified)
        self.leVhost.textEdited.connect(self.virtualHostModofed)        
        self.leCertificatePassword.textEdited.connect(self.certificatePasscodeModified)                
        
        # The following uses textchanged, since it can be typed in or populated.
        # textedited will work, only if the user types in somethin
        self.leCertificateName.textChanged.connect(self.certificateNameModified) 
        self.lePassKey.textChanged.connect(self.passcodekeyFileModified)
        self.leCertificatePassKey.textChanged.connect(self.certificatePasskeyCertFileModified)

    def updatewhost(self, text):
        self.whost.setText(text)

    def httpUrlModified(self, text):
        #print(text)
        self.webUrlModified = True

    def cmdUrlModified(self, text):
        #print(text)
        self.amqpUrlModified = True	

    def userModified(self, text):
        #print(text)
        self.userIdModified = True

    def passcodeModified(self, text):
        #print(text)
        self.passwordModified = True

    def virtualHostModofed(self, text):
        #print(text)
        self.vhostModified = True

    def certificateNameModified(self, text):
        #print(text)
        self.certNameModified = True

    def certificatePasscodeModified(self, text):
        #print(text)
        self.certPassModified = True

    def passcodekeyFileModified(self, text):
         #print(text)
        self.passkeyFileModified = True

    def certificatePasskeyCertFileModified(self, text):
        #print(text)
        self.passkeyCertFileModified = True

    
    def accept(self):
        webUrl = self.leUrl.text().strip()        
        commandUrl = self.le1Url.text().strip()        
        user = self.leUserId.text().strip()
        userPass = self.lePassword.text().strip()
        vHost = self.leVhost.text().strip()
        certName = self.leCertificateName.text().strip()
        certPass = self.leCertificatePassword.text().strip()             

        protocol = True if "https" in webUrl else False
        
        msg =  "Please enter:{nl}Web Url{nl}Amqp Url{nl}User Id{nl}Password{nl}Passkey File and {nl}VHost.{nl}{nl}In case of https, please provide Certificate details.{nl}{nl}" \
               "Please click update setting, before clicking Ok button.".format(nl=os.linesep)

        if webUrl and commandUrl and user and userPass and vHost:
            print(protocol, certName)
            if protocol and len(certName) != 0:
                self._webUrl.emit(webUrl)
                self._commandUrl.emit(commandUrl)
                self._userId.emit(user)

                self._password.emit(self.passKeyFile, userPass)

                self._vhost.emit(vHost)
                self._certName.emit(certName)
                self._certPass.emit(certPass)
                
                self._cancelled.emit(False)

                self.closewin()
            else:
                MessageBox.message(QMessageBox.Information, "RabbitMQ Queue", "Configuration entry issue!", msg)     
                self._cancelled.emit(True)
        else:
            MessageBox.message(QMessageBox.Information, "RabbitMQ Queue", "Configuration entry issue!", msg)     
            self._cancelled.emit(True)
        
    def toggle(self, mode):
        self.connectAction.setEnabled(mode)     
        #self.addSettingAction.setEnabled(mode)
        self.delSettingAction.setEnabled(mode)
        self.updSettingAction.setEnabled(mode)

        self.loginButton.setEnabled(mode)        
        #self.addSettingButton.setEnabled(mode)
        self.delSettingButton.setEnabled(mode)
        self.updSettingButton.setEnabled(mode)    

    def selectionchange(self,index):       
        if index == 0:
            self.leUrl.setText('')
            self.le1Url.setText('')
            self.leUserId.setText('')
            self.lePassword.setText('')
            self.lePassKey.setText('')
            self.leVhost.setText('')
            self.leCertificateName.setText('')
            self.leCertificatePassword.setText('')
            self.leCertificatePassKey.setText('')

            self.leCertificateName.setEnabled(False)
            self.leCertificatePassword.setEnabled(False)
            self.leCertificatePassKey.setEnabled(False)
            self.fileChooser.setEnabled(False)
            self.fileChooserpk.setEnabled(False)
            self.fileChoosercpk.setEnabled(False)

            self.toggle(False)

            self.sessionAvailable = False

            pass              

        if index > 0: 

            section_name = self.leServer.currentText().strip()            
            #print(section_name)
            if section_name == self.parser.get(section_name, 'console.url'):
                self.leUrl.setText(self.parser.get(section_name, 'web.url'))
                self.le1Url.setText(self.parser.get(section_name, 'command.url'))
                self.leUserId.setText(self.parser.get(section_name, 'username'))
                self.lePassword.setText(self.parser.get(section_name, 'password'))

                pkfile = self.parser.get(section_name, 'passkey.file')   
                if pkfile:
                    self.passKeyFile = "{fpath}{file}".format(fpath = "", file=pkfile) 
                    self.lePassKey.setText(self.passKeyFile)

                '''
                if '/' in self.parser.get(section_name, 'vhost'):
                    self.leVhost.setText('')
                else:
                    self.leVhost.setText(self.parser.get(section_name, 'vhost'))    
                '''
                
                self.leVhost.setText(self.parser.get(section_name, 'vhost'))    

                if 'https' in self.parser.get(section_name, 'protocol'):    
                    cname = self.parser.get(section_name, 'certificateName')
                    if cname:
                        certName = "{fpath}{file}".format(fpath = "", file=cname) 
                        self.leCertificateName.setText(certName)

                    self.leCertificatePassword.setText(self.parser.get(section_name, 'certificatePassword'))

                    pkcertfile = self.parser.get(section_name, 'passkeycert.file')
                    if pkcertfile:
                        certpassKey = "{fpath}{file}".format(fpath = "", file=pkcertfile) 
                        self.leCertificatePassKey.setText(certpassKey)

                    self.leCertificateName.setEnabled(True)
                    self.leCertificatePassword.setEnabled(True)
                    self.leCertificatePassKey.setEnabled(True)

                    self.fileChooser.setEnabled(True)
                    self.fileChooserpk.setEnabled(True)
                    self.fileChoosercpk.setEnabled(True)
                else:
                    self.leCertificateName.setText('')
                    self.leCertificatePassword.setText('')
                    self.leCertificatePassKey.setText('')

                    self.leCertificateName.setEnabled(False)
                    self.leCertificatePassword.setEnabled(False)
                    self.leCertificatePassKey.setEnabled(False)

                    self.fileChooser.setEnabled(False)
                    self.fileChooserpk.setEnabled(False)
                    self.fileChoosercpk.setEnabled(False)

                self.toggle(True)     

    def populate(self):
        sections = self.parser.sections()
        self.leServer.addItem("Please Select Server...")
        for section_name in sections:
            if section_name != "OTHER":
                self.leServer.addItem(section_name)    


    def refresh(self):
        self.leServer.clear()        
        
        self.populate()

        self.leUrl.setText('')
        self.le1Url.setText('')
        self.leUserId.setText('')
        self.lePassword.setText('')
        self.lePassKey.setText('')
        self.leVhost.setText('')
        self.leCertificateName.setText('')
        self.leCertificatePassword.setText('')
        self.leCertificatePassKey.setText('')

        self.fileChooser.setEnabled(False)
        self.fileChooserpk.setEnabled(False)
        self.fileChoosercpk.setEnabled(False)
        
        self.toggle(False)        

    def addsetting(self):
        self.createFormGroupBox("add")

        self.leServer.setEditable(True)

        self.delSettingAction.setEnabled(False)
        self.delSettingButton.setEnabled(False)

        vBox = QVBoxLayout()       
        vBox.addWidget(self.formGroupBox)            
        self.widgetadd = QWidget()
        self.widgetadd.setLayout(vBox)        
        self.setCentralWidget(self.widgetadd)   

        if "https" in self.wprotocolCombo.currentText():
            self.leCertificateName.setEnabled(True)
            self.leCertificatePassword.setEnabled(True)
            self.leCertificatePassKey.setEnabled(True)
            self.fileChooser.setEnabled(True)
            self.fileChooserpk.setEnabled(True)
            self.fileChoosercpk.setEnabled(True)
        else:
            self.leCertificateName.setEnabled(False)
            self.leCertificatePassword.setEnabled(False)
            self.leCertificatePassKey.setEnabled(False)
            self.fileChooser.setEnabled(False)
            self.fileChooserpk.setEnabled(False)
            self.fileChoosercpk.setEnabled(False)
    

    def deletesetting(self):
        section_name = self.leServer.currentText()

        self.parser.remove_section(section_name)    
        with open(self.inifile, 'w') as configfile:
            self.parser.write(configfile)

        self.refresh()

        MessageBox.message(QMessageBox.Information, "RabbitMQ Queue", "Configuration entry removed!", \
                                   "Server: {section} removed from File: {file} sucessfully.".format(section=section_name, file=self.inifile))     

    def editsetting(self):

        section_name = self.leServer.currentText()

        if self.webUrlModified:            
            
            self.webUrlModified = False

            url = self.leUrl.text().split(":")
            
            protocol = url[0]
            
            consoleUrl = url[1].replace("/", "").strip()            
            
            portBaseUrl = url[2].split("/")            
            
            port = portBaseUrl[0]

            baseurl = ""
            if len(portBaseUrl) > 1:
                baseurl = "/" + portBaseUrl[1] + "/"
            
            self.parser.set(section_name, 'protocol', protocol)
            self.parser.set(section_name, 'console.url', consoleUrl)
            self.parser.set(section_name, 'console.port', port)
            self.parser.set(section_name, 'console.baseurl', baseurl)
        
        if self.amqpUrlModified:

            self.amqpUrlModified = False

            url = self.le1Url.text().split(":")
            protocol = url[0]            
            amqpUrl = url[1].replace("/", "").strip() 
            amqpPort = url[2]            

            self.parser.set(section_name, 'amqp.protocol', protocol)
            self.parser.set(section_name, 'amqp.url', amqpUrl)
            self.parser.set(section_name, 'amqp.port', amqpPort)
                   
        if self.userIdModified:
            self.userIdModified = False
            self.parser.set(section_name, 'username', self.leUserId.text().strip())

        if self.passkeyFileModified:
            self.passkeyFileModified = False       
            self.parser.set(section_name, 'passkey.file', self.lePassKey.text().strip())

        if self.passwordModified:
            self.passwordModified = False

            passwd = self.lePassword.text()
            #passKeyFile = "{fpath}{file}".format(fpath = self.filePath, file=self.parser.get(section_name, 'passkey.file')) 
            passKeyFile = self.lePassKey.text()

            encPass = ""
            if len(passKeyFile) != 0 and len(passwd) != 0:
                encPass = encrypt.encrypt_password(passKeyFile, passwd)

            self.parser.set(section_name, 'password', encPass)
            
        if self.vhostModified:
            self.vhostModified = False
            self.parser.set(section_name, 'vhost', self.leVhost.text())
        
        if self.certNameModified:
            self.certNameModified = False            
            self.parser.set(section_name, 'certificateName', self.leCertificateName.text())

        if self.passkeyCertFileModified:
            self.passkeyCertFileModified = False
            self.parser.set(section_name, 'passkeycert.file', self.leCertificatePassKey.text().strip())

        if self.certPassModified:               
            self.certPassModified = False

            passwd = self.leCertificatePassword.text()
            #passKeyFile = "{fpath}{file}".format(fpath = self.filePath, file=self.parser.get(section_name, 'passkeycert.file')) 
            #passKeyFile = ".{file}".format(file=self.parser.get(section_name, 'passkeycert.file')) 
            passKeyFile = self.leCertificatePassKey.text()

            encPass = ""
            if len(passKeyFile) != 0 and len(passwd) != 0:
                encPass = encrypt.encrypt_password(passKeyFile, passwd)

            self.parser.set(section_name, 'certificatePassword', encPass)
        
        with open(self.inifile, 'w') as configfile:
            self.parser.write(configfile)

        self.refresh() 

        #index = self.leServer.findText(section_name, Qt.MatchFixedString)
        #if index >= 0:
        #    self.leServer.setCurrentIndex(index)

        
        MessageBox.message(QMessageBox.Information, "RabbitMQ Queue", "Configuration entry updated!", \
                                   "Server: {section} update in File: {file} sucessfully.".format(section=section_name, file=self.inifile))    

    
    def openFileNameDialog(self, fc, action):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog

        title=""
        ftypes=""
        if action == "certname":
            title = "Choose a SSL Certificate"
            ftypes = "PEM Files (*.pem);; All Files(*.*)"
        elif action == "passkey":
            title = "Choose a Password key file"
            ftypes = "TXT Files (*.txt);; All Files(*.*)"
        elif action == "certpasskey":
            title = "Choose a Certificate Password key file"
            ftypes = "TXT Files (*.txt);; All Files(*.*)"

        fileName, _ = QFileDialog.getOpenFileName(self, title, ".",ftypes, options=options)       
        if fileName:
            fc.setText("{fname}".format(fname=fileName.replace(self.filePath, ".")))

    def setReference(self, frame):
        self.frame = frame

    def closewin(self):
        if self is not None:
            self.close()

        if self.frame is not None:
            self.frame.close()

        #self.qapp.exit()      
    
    def closeEvent(self, event):    
        if self is not None:
            self.close()

        if self.frame is not None:
            self.frame.close()
    
        #self.qapp.exit()       