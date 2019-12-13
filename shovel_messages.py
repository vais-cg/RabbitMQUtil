import requests

import json

import decrypt

import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QAction, QHBoxLayout, QPushButton,
QVBoxLayout, QMainWindow, QWidget, QListWidget, QTableView, QAbstractItemView, 
QHeaderView, QLineEdit, QLabel, QGroupBox, QPlainTextEdit, QStatusBar)

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QFont

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize, pyqtSignal

#from login import LoginDialog
from manage_ini import ConnectMenu
from rmqmodel import TableModel
from restFunctions import RestFunctions
from connectAmqp import RabbitMQPikaConnection
from importMessages import ImportMessages

import styles
import windows


__IMAGES_PATH__ = ""

class ShovelMenu(QtWidgets.QMainWindow):

    _refresh = QtCore.pyqtSignal(bool)

    def __init__(self, parser, resources_path):
        #super().__init__()
        super(ShovelMenu, self).__init__()

        __IMAGES_PATH__ = resources_path + '/images'
		
        self.setWindowTitle("RabbitMQ Utility - Shovel Messages")    # Set the window title

        #self.setWindowIcon(QtGui.QIcon(__IMAGES_PATH__ + '/rabbit_icon.jpg'))      

        #------------------------------
        #self.app = app
        self._webUrl = ""
        self._commandUrl = ""
        self._userId = ""
        self._password = ""
        self._vhost = ""
        self._certName = ""
        self._certPass = ""
        self._cancelled = True

        self._exportFileName = ""

        self.sessionAvailable = False

        self.session = None        

        self.shovelConnection = None

        self.messages = None

        self.frame = None

        self.propertyadd = False
        self.headeradd = False

        self.eitems = None

        self.parser = parser

        self.parser.read(os.environ['RMQ_COMMON_INI_FILE'])
        section_name = "DEFAULT"
        self.filteredVhosts = self.parser.get(section_name, 'filter.vhosts').split(",")
        self.filteredVhosts = [item.lower().strip() for item in self.filteredVhosts if item]

        #print("self.filteredVhosts:{}".format(self.filteredVhosts))
        #------------------------------ 
        self.qapp = QApplication([])
        #V = self.qapp.desktop().screenGeometry()
        #h = V.height() - 600 
        #w = V.width() - 600

        h = 800 
        w = 800

        self.resize(w, h)        
               
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)  

        #self.login = LoginDialog(self.parser)
        self.login = ConnectMenu(self.parser, resources_path)

        self.login._cancelled.connect(self.loginCancelled)

        self.login._webUrl.connect(self.getWebConnectionUrl)
        self.login._commandUrl.connect(self.getCommandConnectionUrl)
        self.login._userId.connect(self.getConnectionUser)
        self.login._password.connect(self.getConnectionPassword)
        self.login._vhost.connect(self.getCconnectionVhost)
        self.login._certName.connect(self.getConnectionCertName)
        self.login._certPass.connect(self.getConnectionCertPass)

        #styles.light(self.qapp)
        self.loginmw = windows.ModernWindow(self.login, self.parser)

        self.widget = QWidget()

        self.fromParent = False

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        #----------------------------------------- MENU BAR -------------------------------------------------
        # Create Connect
        self.connectAction = QAction(QIcon(__IMAGES_PATH__ + '/connect.png'), '&Connect', self)        
        self.connectAction.setShortcut('ALT+C')
        self.connectAction.setStatusTip('Connect')
        self.connectAction.triggered.connect(self.show_login)
        self.connectAction.setEnabled(False)

        # Create Disconnect
        self.disconnectAction = QAction(QIcon(__IMAGES_PATH__ + '/disconnect.png'), '&DisConnect', self)        
        self.disconnectAction.setShortcut('ALT+D')
        self.disconnectAction.setStatusTip('Disconnect')
        self.disconnectAction.triggered.connect(self.disconnect)
        
        # Create Refresh
        self.refreshAction = QAction(QIcon(__IMAGES_PATH__ + '/refresh.png'), '&Refresh', self)        
        self.refreshAction.setShortcut('ALT+D')
        self.refreshAction.setStatusTip('Refresh')
        self.refreshAction.triggered.connect(self.refresh)

         # Create Exit action
        self.exitAction = QAction(QIcon(__IMAGES_PATH__ + '/terminate.png'), '&Exit', self)        
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.closewin)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.connectAction)
        fileMenu.addAction(self.disconnectAction)
        fileMenu.addAction(self.refreshAction)
        fileMenu.addAction(self.exitAction)
        
        self.toolbar = self.addToolBar('')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)

        #self.toolbar.setIconSize(QSize(50,50))
        #self.toolbar.setGeometry(100, 100, 400, 400)

        #------------ Connect -------------
        self.loginButton = QAction(QIcon(__IMAGES_PATH__ + '/connect.png'), '&Connect', self)
        self.loginButton.setIconText('Connect')
        self.loginButton.triggered.connect(self.show_login)
        self.toolbar.addAction(self.loginButton)

        self.loginButton.setEnabled(False)

        #------------ Refresh -------------
        self.refreshButton = QAction(QIcon(__IMAGES_PATH__ + '/refresh.png'), '&Refresh', self)
        self.refreshButton.triggered.connect(self.refresh)
        self.toolbar.addAction(self.refreshButton)         

        self.toolbar.addSeparator()

        #------------ Disconnect -------------
        self.disconnectButton = QAction(QIcon(__IMAGES_PATH__ + '/disconnect.png'), '&Disconnect', self)
        self.disconnectButton.triggered.connect(self.disconnect)
        self.toolbar.addAction(self.disconnectButton)         

        
        #------------ Exit -------------
        self.exitButton = QAction(QIcon(__IMAGES_PATH__ + '/terminate.png'), '&Exit', self)
        self.exitButton.triggered.connect(self.closewin)        
        self.toolbar.addAction(self.exitButton)         

        self.xgroupBox = QGroupBox("Exchanges")

        self.exchange_list = QListWidget()
        self.exchange_list.itemSelectionChanged.connect(self.populateQueues)
        
        self.rkgroupBox = QGroupBox("Routing Key")
        self.routingKey_list = QListWidget()

        self.argGroupBox = QGroupBox("Arguments")
        self.argument_list = QListWidget()
        
        #-------- Exchange and Queue List ---------------
        hbox = QHBoxLayout()
        
        #-----------------------------------------------
        vboxexsub = QVBoxLayout()
        
        hboxexsub = QHBoxLayout()

        self.exlistsearch = QLineEdit()
        self.exlistsearch.textEdited.connect(lambda: self.searchItem(self.exchange_list, self.exlistsearch.text(), self.e_items))
        self.exlistsearch.returnPressed.connect(lambda: self.searchItem(self.exchange_list, self.exlistsearch.text(), self.e_items))
        
        hboxexsub.addWidget(QLabel("Search Exchange(s):"))
        hboxexsub.addWidget(self.exlistsearch) 
        
        vboxexsub.addLayout(hboxexsub) 
        vboxexsub.addWidget(self.exchange_list) 
            
        self.xgroupBox.setLayout(vboxexsub)

        hbox.addWidget(self.xgroupBox)
        #-----------------------------------------------
        vboxsub1 = QVBoxLayout()

        hboxsub1 = QHBoxLayout()

        self.rklistsearch = QLineEdit()
        self.rklistsearch.textEdited.connect(lambda: self.searchItem(self.routingKey_list, self.rklistsearch.text(), self.rklst))
        self.rklistsearch.returnPressed.connect(lambda: self.searchItem(self.routingKey_list, self.rklistsearch.text(), self.rklst))
        
        
        hboxsub1.addWidget(QLabel("Search Routing Key:"))
        hboxsub1.addWidget(self.rklistsearch)

        vboxsub1.addLayout(hboxsub1) 
        vboxsub1.addWidget(self.routingKey_list)
        self.rkgroupBox.setLayout(vboxsub1)
         
        hbox.addWidget(self.rkgroupBox)
        #-----------------------------------------------
        vboxsub2 = QVBoxLayout()
        
        hboxsub2 = QHBoxLayout()
        
        self.argslistsearch = QLineEdit()
        self.argslistsearch.textEdited.connect(lambda: self.searchItem(self.argument_list, self.argslistsearch.text(), self.arglst))
        self.argslistsearch.returnPressed.connect(lambda: self.searchItem(self.argument_list, self.argslistsearch.text(), self.arglst))

        hboxsub2.addWidget(QLabel("Search Arguments:"))
        hboxsub2.addWidget(self.argslistsearch)

        vboxsub2.addLayout(hboxsub2) 
        vboxsub2.addWidget(self.argument_list)
        self.argGroupBox.setLayout(vboxsub2)
        self.argument_list.itemSelectionChanged.connect(self.populateHeaders)

        hbox.addWidget(self.argGroupBox)
        #-----------------------------------------------
        
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)

        '''
        #-------------- Routing Key -----------------
        hbox2 = QHBoxLayout()
        self.rkLabel = QLabel("Routing Key")
        self.rkText = QLineEdit()
        hbox2.addWidget(self.rkLabel)
        hbox2.addWidget(self.rkText)
        
        vbox.addLayout(hbox2)
        '''

        #-------------- Properties and Headers --------------
        self.propertiesGroupBox = QGroupBox("Properties")

        hboxpropheader = QHBoxLayout()

        vboxproptable = QVBoxLayout()

        hboxbuttonprop = QHBoxLayout()        

        self.propAddButton = QPushButton("")
        self.propDelButton = QPushButton("")

        self.propAddButton.setIcon(QIcon(__IMAGES_PATH__ + '/addrow.png'))
        self.propAddButton.setIconSize(QSize(25,25))

        self.propDelButton.setIcon(QIcon(__IMAGES_PATH__ + '/deleterow.png'))
        self.propDelButton.setIconSize(QSize(25,25))

        self.propAddButton.setObjectName('addPropertyKey')
        self.propDelButton.setObjectName('delPropertyKey')
        self.propDelButton.setEnabled(False)
        self.propAddButton.clicked.connect(self.buttonClicked)
        self.propDelButton.clicked.connect(self.buttonClicked)

        hboxbuttonprop.addWidget(QLabel("      "))
        hboxbuttonprop.addWidget(QLabel("      "))
        hboxbuttonprop.addWidget(QLabel("      "))
        hboxbuttonprop.addWidget(QLabel("      "))
        hboxbuttonprop.addWidget(self.propAddButton)
        hboxbuttonprop.addWidget(self.propDelButton)
        
        headers = ["Key", "Value"]       
        datain = []

        self.proptablemodel = TableModel(datain, headers, self)
        self.proptablemodelview = QTableView()  
        self.proptablemodelview.setSelectionMode(QAbstractItemView.SingleSelection)   
        
        self.proptablemodelview.clicked.connect(self.showTableSelectedRowColumn)

        self.set_table_view_attributes(self.proptablemodelview, self.proptablemodel, datain)        
        
        #vboxproptable.addWidget(self.proptablemodelview)
        self.propertiesGroupBox.setLayout(vboxproptable)

        vboxproptable.addLayout(hboxbuttonprop)
        vboxproptable.addWidget(self.proptablemodelview)

        vboxheadtable = QVBoxLayout()

        self.headersGroupBox = QGroupBox("Headers")

        hboxbuttonheader = QHBoxLayout()        
        self.headerAddButton = QPushButton("")
        self.headerDelButton = QPushButton("")

        self.headerAddButton.setIcon(QIcon(__IMAGES_PATH__ + '/addrow.png'))
        self.headerAddButton.setIconSize(QSize(25,25))

        self.headerDelButton.setIcon(QIcon(__IMAGES_PATH__ + '/deleterow.png'))
        self.headerDelButton.setIconSize(QSize(25,25))

        self.headerAddButton.setObjectName('addHeaderKey')
        self.headerDelButton.setObjectName('delHeaderKey')

        self.headerDelButton.setEnabled(False)
        self.headerAddButton.clicked.connect(self.buttonClicked)
        self.headerDelButton.clicked.connect(self.buttonClicked)

        hboxbuttonheader.addWidget(QLabel("      "))
        hboxbuttonheader.addWidget(QLabel("      "))
        hboxbuttonheader.addWidget(QLabel("      "))
        hboxbuttonheader.addWidget(QLabel("      "))
        hboxbuttonheader.addWidget(self.headerAddButton)
        hboxbuttonheader.addWidget(self.headerDelButton)

        message_header = ["Key", "Value"]
        messageData = []
        self.headertablemodel = TableModel(messageData, message_header, self)
        self.headertablemodelview = QTableView()            
        self.headertablemodelview.setSelectionMode(QAbstractItemView.MultiSelection)
      
        self.headertablemodelview.clicked.connect(self.showTableSelectedRowColumn)

        self.set_table_view_attributes(self.headertablemodelview, self.headertablemodel, messageData)

        vboxheadtable.addLayout(hboxbuttonheader)        
        vboxheadtable.addWidget(self.headertablemodelview)

        self.headersGroupBox.setLayout(vboxheadtable)

        hboxpropheader.addWidget(self.propertiesGroupBox)
        hboxpropheader.addWidget(self.headersGroupBox)

        vbox.addLayout(hboxpropheader)

        #----------------- Message to be Shoveled --------------------------------

        hboxMessage = QHBoxLayout()        

        self.qpShoveledMessages = QPlainTextEdit(self)
        self.qpShoveledMessages.resize(500, 500)        
        self.qpShoveledMessages.setStyleSheet(
        """QPlainTextEdit {background-color: #333;
                           color: #00FF00;
                           font-family: Courier;}""")

        #self.qpShoveledMessages.setEnabled(False)

        hboxMessage.addWidget(self.qpShoveledMessages)
        
        vbox.addLayout(hboxMessage)

        #--------------------- Publish and Cancel Button -------------------------

        buttonHeader = QHBoxLayout()
        publishButton = QPushButton("Shovel Message")
        publishButton.setIcon(QIcon(__IMAGES_PATH__ + '/publish.png'))
        publishButton.setIconSize(QSize(25,25))

        cancelButton = QPushButton("Cancel")
        cancelButton.setIcon(QIcon(__IMAGES_PATH__ + '/cancel.png'))
        cancelButton.setIconSize(QSize(25,25))

        publishButton.setObjectName('publish')
        publishButton.clicked.connect(self.buttonClicked)

        cancelButton.clicked.connect(self.closewin)

        buttonHeader.addWidget(QLabel("         "))
        buttonHeader.addWidget(QLabel("         "))
        buttonHeader.addWidget(QLabel("         "))
        buttonHeader.addWidget(QLabel("         "))
        buttonHeader.addWidget(publishButton)
        buttonHeader.addWidget(cancelButton)

        vbox.addLayout(buttonHeader)

        self.widget.setLayout(vbox)
        
        self.setCentralWidget(self.widget)
        
    def set_table_view_attributes(self, table_view, table_model, data):     
        
        table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_view.setAlternatingRowColors(True)
        table_view.setModel(table_model)        
        table_view.setSortingEnabled(True)         
              

        # hide vertical header
        vh = table_view.verticalHeader()
        vh.setVisible(False)
        #vh.setSectionResizeMode(QHeaderView.Stretch)
        #vh.setDefaultSectionSize(75)
        
        hh = table_view.horizontalHeader()
        #hh.setSectionResizeMode(QHeaderView.Stretch)
        hh.setStretchLastSection(True)
        hh.setSectionsClickable(True)
        hh.setHighlightSections(True)

    def show_login(self):
        self.login.show()       
        self.loginmw.show()
        self.login.setReference(self.loginmw)
	
    def loginCancelled(self, cancelled):
        self._cancelled = cancelled
        #print(self._cancelled)

        if self._cancelled == False:
            self.session = requests.Session() 
            self.sessionAvailable = True 

            self.disconnect()

            self.populate()  
                        
            #print("self.shovelConnection = {}".format(self.shovelConnection))

            if self.shovelConnection is None:
                self.shovelConnection = RabbitMQPikaConnection.connect(RabbitMQPikaConnection, self, self._commandUrl, self._userId, self._password, self._certName, self._vhost, 'RabbitMQ_Util_Shovel')                
            
            self.connectAction.setEnabled(False)
            self.loginButton.setEnabled(False)

    def getWebConnectionUrl(self, url):
        self._webUrl = url
        #print(url)

    def getCommandConnectionUrl(self, url):
        self._commandUrl = url
        #print(url)

    def getConnectionUser(self, user):
        self._userId = user
        #print(user)

    def getConnectionPassword(self, passkeyFile, password):
        decPass = decrypt.decrypt_password(passkeyFile, password.encode())
        self._password = decPass
        #print(self._password)
        #print("*************************************")

    def getCconnectionVhost(self, vhost):
        self._vhost = vhost
        #print(vhost)

    def getConnectionCertName(self, cert):
        self._certName = cert
        #print(cert)

    def getConnectionCertPass(self, certpass):
        self._certPass = certpass        
        if certpass is not None:
            #print(certpass)
            #print("************************************")
            pass
    
    def prettyPrintJson(self, val, sort=True, indents=4):
        if type(val) is str:
            return json.dumps(json.loads(val), sort_keys=sort, indent=indents)
        else:
            return json.dumps(val, sort_keys=sort, indent=indents)
        return None

    def populateQueues(self):

        self.rklst = []
        self.arglst = []

        self.routingKey_list.clear()
        self.argument_list.clear()
        self.headertablemodelview.model().changeData([])

        data = RestFunctions.exchange_bindings(RestFunctions, self, self.session, self._webUrl, self.exchange_list.currentItem().text(), self._userId, self._password, self._certName)    

        for item in data:            
            #print(item[4], item[6])
            rkey = item[6]
            args = item[7]

            if len(rkey) > 0:
                self.routingKey_list.addItem(str(rkey))  
                self.rklst.append(str(rkey))

            if len(args) > 0:
                self.argument_list.addItem(str(args))  
                self.arglst.append(str(args))
           
        '''if self.routingKey_list.count() > 0:
            self.routingKey_list.setCurrentRow(0)
    
        if self.argument_list.count() > 0:
            self.argument_list.setCurrentRow(0)'''


    def populateHeaders(self):
        headerArray = []
        args = self.argument_list.currentItem().text().split(",")
        for element in args:
            content = element.split(":")
            headerArray.append(content)
        
        self.headertablemodelview.model().changeData(headerArray)

    def showTableSelectedRowColumn(self, index):
        if self.propertyadd:
            self.propDelButton.setEnabled(True)

        if self.headeradd:
            self.headerDelButton.setEnabled(True)

        self.tableSelectedRow = index.row()
        self.tableSelectedColumn = index.column()
        
    def buttonClicked(self):
        button = self.sender()
        #print(button.objectName())
        
        if not button: return  

        buttonObjectName = button.objectName()

        propTableModel = self.proptablemodelview.model()
        headerTableModel = self.headertablemodelview.model()

        if buttonObjectName == "addPropertyKey":
            data = [[]]
            self.addRow(propTableModel, data)
            self.propertyadd = True
        elif buttonObjectName == "delPropertyKey":
            if self.tableSelectedRow is not None:
                del propTableModel.arraydata[self.tableSelectedRow]
                propTableModel.changeData(propTableModel.arraydata)
               
                self.propDelButton.setEnabled(False)
        elif buttonObjectName == "addHeaderKey":
            data1 = [[]]
            self.addRow(headerTableModel, data1)
            self.headeradd = True
        elif buttonObjectName == "delHeaderKey": 
            if self.tableSelectedRow is not None:
                del headerTableModel.arraydata[self.tableSelectedRow]
                headerTableModel.changeData(headerTableModel.arraydata)
               
                self.headerDelButton.setEnabled(False)
        elif buttonObjectName == "publish":
            
            exchange = "" if len(self.exchange_list.selectedItems()) == 0 else self.exchange_list.currentItem().text()
                        
            routingKey = "" if len(self.routingKey_list.selectedItems()) == 0 else self.routingKey_list.currentItem().text()

            propTableModel.removeRowsWithEmptyColumns()
            properties = dict(propTableModel.arraydata)

            headerTableModel.removeRowsWithEmptyColumns()                        
            headers = dict(headerTableModel.arraydata)
                      
            properties['headers'] = headers
            
            #print("shovel conn: {}".format(self.shovelConnection))
            #ImportMessages.shovelMessages(ImportMessages, exchange, routingKey, properties, self.messages, self.sessionAvailable, self.shovelConnection, self.qpShoveledMessages.toPlainText())
            ImportMessages.shovelMessages(ImportMessages, exchange, routingKey, properties, self.qpShoveledMessages.toPlainText(), self.sessionAvailable, self.shovelConnection, self.qpShoveledMessages.toPlainText())

            # self._refresh.emit(True)

    def searchItem(self, listWidgetName, search_string, eraitems):
        
        items = [item for item in eraitems if search_string in item] 
        
        if len(items) > 0:
            listWidgetName.clear()
            listWidgetName.addItems(items)
        else:
            #listWidgetName.setSelectionMode(QAbstractItemView.SingleSelection)    
            listWidgetName.clear()   
            for item in eraitems:  
                listWidgetName.addItem(str(item))

    '''
    def del_none_or_empty_keys(self, dict):
        for elem in dict.keys():
            if dict[elem] == None:
                del dict[elem]
    '''            

    def addRow(self, table_model, data):
        rowcount = table_model.rowCount()
        if rowcount == 0:
            table_model.update(rowcount, data) 
        else:
            if len(table_model.arraydata[rowcount - 1][0]) != 0:
                table_model.update(rowcount, data) 

    def setMessage(self, msgdata, frame):
        self.frame = frame

        messages =  json.loads(msgdata)
        self.shovelMessage = {}

        for key in messages:                    
            message = messages[key]['body']
            col = { 'body': message } 
            self.shovelMessage[key] = col    
        
        msg = json.dumps(self.shovelMessage, sort_keys=True, indent=4)

        self.qpShoveledMessages.setPlainText(msg)
        self.messages = messages

    def refresh(self):
        self.reset()        
        self.populate()

    def setConnection(self, connection, sessionAvailable, session, _webUrl, _userId, _password, _certName):
        
        self.fromParent = True

        self.shovelConnection = connection

        #print("From rmq main - self.shovelConnection = {}".format(self.shovelConnection))

        self.sessionAvailable = sessionAvailable
        self.session = session
        self._webUrl = _webUrl
        self._userId = _userId
        self._password = _password
        self._certName = _certName

        self.reset()

        self.populate()

    def populate(self):
        self.e_items = []

        self.eitems = RestFunctions.exchange_list(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)
        self.exchange_list.clear()
        for item in self.eitems:
            name = item["name"]
            if any(filteredVhost in name for filteredVhost in self.filteredVhosts) or not self.filteredVhosts:
                if(len(name) != 0):
                    if len(name) == 0:
                        self.exchange_list.addItem("Default")
                        self.e_items.append("Default")
                    elif "federation" not in str(name):
                        self.exchange_list.addItem(str(name))        
                        self.e_items.append(str(name))

    def reset(self):
        self.exchange_list.clear()
        self.routingKey_list.clear() 
        self.argument_list.clear()        
        
        propData = []
        self.proptablemodelview.model().changeData(propData)

        headerData = []
        self.headertablemodelview.model().changeData(headerData)

    def disconnect(self):        

        self.reset()

        if self.session is not None:
            print("Closing Request Session - Shovel Messages")
            self.session.close()

        if self.login is not None:
            print("Closing Connection Information Dialog - Shovel Messages")
            self.login.close()

        if self.shovelConnection is not None and not self.fromParent:            
            print("Closing AMQP Connection - Shovel Messages")
            self.shovelConnection.close()
        else:    
            self.shovelConnection = None

        self.connectAction.setEnabled(True)
        self.loginButton.setEnabled(True)
    
    def closewin(self):
        if self is not None:
            self.close()

        if self.frame is not None:
            self.frame.close()

        self.login.close()
        self.loginmw.close()

        if self.shovelConnection is not None and self.shovelConnection.is_open:
            self.shovelConnection.close()

        if self.session is not None:
            self.session.close()

        #self.qapp.exit()        
    
    def closeEvent(self, event):    
        
        if self is not None:
            self.close()
        
        if self.frame is not None:
            self.frame.close()

        self.login.close()
        self.loginmw.close()

        if self.shovelConnection is not None and self.shovelConnection.is_open:
            self.shovelConnection.close()

        if self.session is not None:
            self.session.close()
        
        #self.qapp.exit()        
