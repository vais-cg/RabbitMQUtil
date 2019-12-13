import requests

#import os

import decrypt

from configparser import ConfigParser

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QAction, QFormLayout, QHBoxLayout, QPushButton,
QVBoxLayout, QMainWindow, QWidget, QTableView, QAbstractItemView, QHeaderView, QLineEdit, QLabel, QGroupBox,  
QComboBox, QRadioButton, QStatusBar, QMessageBox)

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QFont

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize, pyqtSignal

#from login import LoginDialog
from manage_ini import ConnectMenu

from rmqmodel import TableModel

from restFunctions import RestFunctions

from connectAmqp import RabbitMQPikaConnection

from messagebox import MessageBox

import styles
import windows


__IMAGES_PATH__ = ""

class ExchangeQueuesBindingsMenu(QtWidgets.QMainWindow):

    _refresh = QtCore.pyqtSignal(bool)

    def __init__(self, parser, resources_path):
        #super().__init__()
        super(ExchangeQueuesBindingsMenu, self).__init__()

        __IMAGES_PATH__ = resources_path + '/images'

        self.setWindowTitle("RabbitMQ Utility - Add Exchange/Queues/Bindings")    # Set the window title

        #self.setWindowIcon(QtGui.QIcon(__IMAGES_PATH__ + '/rabbit_icon.jpg'))

        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)  
        #------------------------------
        #self.app = app

        self.sessionAvailable = False

        self.session = None        

        self.eqbConnection = None

        self.elist = None
        self.qlist = None

        self.exchangeadd = False
        self.queueadd = False
        self.bindadd = False

        self.parser = parser
        #------------------------------ 
        self.qapp = QApplication([])
        #V = self.qapp.desktop().screenGeometry()
        #h = V.height() - 600 
        #w = V.width() - 600

        h = 800 
        w = 800

        self.resize(w, h)

        #self.login = LoginDialog(self.parser)
        self.login = ConnectMenu(self.parser, resources_path)

        self.login._cancelled.connect(self.loginCancelled)

        self.login._webUrl.connect(self.getWebConnectionUrl)
        self.login._commandUrl.connect(self.getCommandConnectionUrl)
        self.login._userId.connect(self.getConnectionUser)
        self.login._password.connect(self.getConnectionPassword)
        self.login._vhost.connect(self.getConnectionVhost)
        self.login._certName.connect(self.getConnectionCertName)
        self.login._certPass.connect(self.getConnectionCertPass)

        self.loginmw = windows.ModernWindow(self.login, self.parser)

        self.widget = QWidget()

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.fromParent = False

        self.frame = None

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
        self.loginButton.setEnabled(False)
        self.loginButton.setStatusTip("Click here to login into server") 
        self.toolbar.addAction(self.loginButton)

        #------------ Refresh -------------
        self.refreshButton = QAction(QIcon(__IMAGES_PATH__ + '/refresh.png'), '&Refresh', self)
        self.refreshButton.triggered.connect(self.refresh)
        self.refreshButton.setStatusTip("Click here to refresh data") 
        self.toolbar.addAction(self.refreshButton)         

        self.toolbar.addSeparator()

        #------------ Disconnect -------------
        self.disconnectButton = QAction(QIcon(__IMAGES_PATH__ + '/disconnect.png'), '&Disconnect', self)
        self.disconnectButton.triggered.connect(self.disconnect)
        self.disconnectButton.setStatusTip("Click here to disconnect from server") 
        self.toolbar.addAction(self.disconnectButton)         

        
        #------------ Exit -------------
        self.exitButton = QAction(QIcon(__IMAGES_PATH__ + '/terminate.png'), '&Exit', self)
        self.exitButton.triggered.connect(self.closewin)     
        self.exitButton.setStatusTip("Click here to close and exit this application")    
        self.toolbar.addAction(self.exitButton)         
    
        
        vBoxEQB = QVBoxLayout()    

        #---------------- Top ----------------------------------
        hboxEQB1 = QHBoxLayout()
        vboxEx = QVBoxLayout()
        vboxQ = QVBoxLayout()

        self.xgroupBox = QGroupBox("Add a new exchange")

        layoutEx = QFormLayout()

        self.evhostLabel = QLabel("Virtual Host:")
        self.evhost = QComboBox()
        
        self.exNameLabel = QLabel("Name:")
        self.exName = QLineEdit()
        self.exName.textChanged[str].connect(lambda: self.addExchangeButton.setEnabled(self.exName.text() != ""))
        self.exName.textChanged[str].connect(lambda: self.delExchangeButton.setEnabled(self.exName.text() != ""))

        self.exTypeLabel = QLabel("Type:")
        self.exType = QComboBox()
        self.durabilityLabel = QLabel("Durability")
        self.durability = QComboBox()
        self.durability.addItem("Durable")
        self.durability.addItem("Transient")

        self.autoDeleteLabel = QLabel("Auto Delete?:")
        self.autoDelete = QComboBox()
        self.autoDelete.addItem("No")
        self.autoDelete.addItem("Yes")

        self.internalLabel = QLabel("Internal?:")
        self.internal = QComboBox()
        self.internal.addItem("No")
        self.internal.addItem("Yes")

        self.addExchangeButton = QPushButton("Add exchange")
        self.addExchangeButton.setObjectName('addExchange')
        self.addExchangeButton.clicked.connect(self.buttonClicked)
        self.addExchangeButton.setEnabled(False)

        self.delExchangeButton = QPushButton("Delete exchange")
        self.delExchangeButton.setObjectName('delExchange')
        self.delExchangeButton.clicked.connect(self.buttonClicked)
        self.delExchangeButton.setEnabled(False)

        self.exArgsGroupBox = QGroupBox("Arguments")
        
        vboxexargstable = QVBoxLayout()

        hboxbuttonexargs = QHBoxLayout()        

        self.exArgsAddButton = QPushButton("")
        self.exArgsDelButton = QPushButton("")

        self.exArgsAddButton.setIcon(QIcon(__IMAGES_PATH__ + '/addrow.png'))
        self.exArgsAddButton.setIconSize(QSize(25,25))

        self.exArgsDelButton.setIcon(QIcon(__IMAGES_PATH__ + '/deleterow.png'))
        self.exArgsDelButton.setIconSize(QSize(25,25))

        self.exArgsAddButton.setObjectName('addExArgsKey')
        self.exArgsDelButton.setObjectName('delExArgsKey')
        self.exArgsDelButton.setEnabled(False)
        self.exArgsAddButton.clicked.connect(self.buttonClicked)
        self.exArgsDelButton.clicked.connect(self.buttonClicked)

        hboxbuttonexargs.addWidget(QLabel("      "))
        hboxbuttonexargs.addWidget(QLabel("      "))
        hboxbuttonexargs.addWidget(QLabel("      "))
        hboxbuttonexargs.addWidget(QLabel("      "))
        hboxbuttonexargs.addWidget(self.exArgsAddButton)
        hboxbuttonexargs.addWidget(self.exArgsDelButton)
        
        vboxexargstable.addLayout(hboxbuttonexargs)

        headers = ["Key", "Value"]       
        datainex = []

        self.exargstablemodel = TableModel(datainex, headers, self)
        self.exargstablemodelview = QTableView()  
        self.exargstablemodelview.setSelectionMode(QAbstractItemView.SingleSelection)   
        
        self.exargstablemodelview.clicked.connect(self.showTableSelectedRowColumn)

        self.set_table_view_attributes(self.exargstablemodelview, self.exargstablemodel, datainex)        
        
        vboxexargstable.addWidget(self.exargstablemodelview)               

        self.exArgsGroupBox.setLayout(vboxexargstable)

        layoutEx.addRow(self.evhostLabel, self.evhost)
        layoutEx.addRow(self.exNameLabel, self.exName)
        layoutEx.addRow(self.exTypeLabel, self.exType)
        layoutEx.addRow(self.durabilityLabel, self.durability)
        layoutEx.addRow(self.autoDeleteLabel, self.autoDelete)
        layoutEx.addRow(self.internalLabel, self.internal)
        layoutEx.addRow(self.exArgsGroupBox)

        exbuttonlayout = QHBoxLayout()
        exbuttonlayout.addWidget(self.addExchangeButton)
        exbuttonlayout.addWidget(self.delExchangeButton)
        exbuttonlayout.addWidget(QLabel(""))

        layoutEx.addRow(exbuttonlayout)        

        self.xgroupBox.setLayout(layoutEx)

        vboxEx.addWidget(self.xgroupBox)
        hboxEQB1.addLayout(vboxEx, 0)

        #------------- Queue --------------------------------------------
        
        self.qgroupBox = QGroupBox("Add a new queue")

        layoutQ = QFormLayout()

        self.qvhostLabel = QLabel("Virtual Host:")
        self.qvhost = QComboBox()
        
        self.qNameLabel = QLabel("Name:")
        self.qName = QLineEdit()
        self.qName.textChanged[str].connect(lambda: self.addQueueButton.setEnabled(self.qName.text() != ""))
        self.qName.textChanged[str].connect(lambda: self.delQueueButton.setEnabled(self.qName.text() != ""))
        self.qName.textChanged[str].connect(lambda: self.purgeQueueButton.setEnabled(self.qName.text() != ""))

        #self.qNodeLabel = QLabel("Node:")
        #self.qNode = QComboBox()
        
        self.qDurabilityLabel = QLabel("Durability")
        self.qDurability = QComboBox()
        self.qDurability.addItem("Durable")
        self.qDurability.addItem("Transient")

        self.qAutoDeleteLabel = QLabel("Auto Delete?:")
        self.qAutoDelete = QComboBox()
        self.qAutoDelete.addItem("No")
        self.qAutoDelete.addItem("Yes")

        self.addQueueButton = QPushButton("Add queue")
        self.addQueueButton.setObjectName('addQueue')
        self.addQueueButton.clicked.connect(self.buttonClicked)
        self.addQueueButton.setEnabled(False)

        self.delQueueButton = QPushButton("Delete queue")
        self.delQueueButton.setObjectName('delQueue')
        self.delQueueButton.clicked.connect(self.buttonClicked)
        self.delQueueButton.setEnabled(False)

        self.purgeQueueButton = QPushButton("Purge queue")
        self.purgeQueueButton.setObjectName('purgeQueue')
        self.purgeQueueButton.clicked.connect(self.buttonClicked)
        self.purgeQueueButton.setEnabled(False)

        self.qArgsGroupBox = QGroupBox("Arguments")

        vboxqargstable = QVBoxLayout()

        hboxbuttonqargs = QHBoxLayout()        

        self.qArgsAddButton = QPushButton("")
        self.qArgsDelButton = QPushButton("")

        self.qArgsAddButton.setIcon(QIcon(__IMAGES_PATH__ + '/addrow.png'))
        self.qArgsAddButton.setIconSize(QSize(25,25))

        self.qArgsDelButton.setIcon(QIcon(__IMAGES_PATH__ + '/deleterow.png'))
        self.qArgsDelButton.setIconSize(QSize(25,25))

        self.qArgsAddButton.setObjectName('addQArgsKey')
        self.qArgsDelButton.setObjectName('delQArgsKey')
        self.qArgsDelButton.setEnabled(False)
        self.qArgsAddButton.clicked.connect(self.buttonClicked)
        self.qArgsDelButton.clicked.connect(self.buttonClicked)

        hboxbuttonqargs.addWidget(QLabel("      "))
        hboxbuttonqargs.addWidget(QLabel("      "))
        hboxbuttonqargs.addWidget(QLabel("      "))
        hboxbuttonqargs.addWidget(QLabel("      "))
        hboxbuttonqargs.addWidget(self.qArgsAddButton)
        hboxbuttonqargs.addWidget(self.qArgsDelButton)

        vboxqargstable.addLayout(hboxbuttonqargs)

        headers = ["Key", "Value"]       
        datainq = []

        self.qargstablemodel = TableModel(datainq, headers, self)
        self.qargstablemodelview = QTableView()  
        self.qargstablemodelview.setSelectionMode(QAbstractItemView.SingleSelection)   

        self.qargstablemodelview.clicked.connect(self.showTableSelectedRowColumn)

        self.set_table_view_attributes(self.qargstablemodelview, self.qargstablemodel, datainq)               
        
        vboxqargstable.addWidget(self.qargstablemodelview)

        self.qArgsGroupBox.setLayout(vboxqargstable)

        layoutQ.addRow(self.qvhostLabel, self.qvhost)
        layoutQ.addRow(self.qNameLabel, self.qName)
        layoutQ.addRow(self.qDurabilityLabel, self.qDurability)
        #layoutQ.addRow(self.qNodeLabel, self.qNode)        
        layoutQ.addRow(self.qAutoDeleteLabel, self.qAutoDelete)
        layoutQ.addRow(QLabel(""), QLabel(""))
        layoutQ.addRow(QLabel(""), QLabel(""))
        layoutQ.addRow(self.qArgsGroupBox)

        qbuttonlayout = QHBoxLayout()
        qbuttonlayout.addWidget(self.addQueueButton)
        qbuttonlayout.addWidget(self.delQueueButton)
        qbuttonlayout.addWidget(self.purgeQueueButton)

        layoutQ.addRow(qbuttonlayout)

        self.qgroupBox.setLayout(layoutQ)

        vboxQ.addWidget(self.qgroupBox)
        hboxEQB1.addLayout(vboxQ, 0)

        #-------------------  Bottom ----------------------
        hboxEQB2 = QHBoxLayout()
        
        layoutBinding = QFormLayout()

        self.bindinggroupBox = QGroupBox("Add a new binding")
        
        self.exchange2queue = QRadioButton("Exchange to Queue")
        self.exchange2exchange = QRadioButton("Exchange to Exchange")

        self.exchange2queue.setChecked(True)

        self.exchange2queue.toggled.connect(lambda:self.btnstate(self.exchange2queue))
        self.exchange2exchange.toggled.connect(lambda:self.btnstate(self.exchange2exchange))

        self.sourceLabel = QLabel("Source:")
        self.source = QComboBox()

        self.targetLabel = QLabel("Target:")
        self.target = QComboBox()
        
        self.target.currentIndexChanged['QString'].connect(lambda: self.addBindButton.setEnabled(self.target.currentText() != self.source.currentText()))
        self.target.currentIndexChanged['QString'].connect(lambda: self.addUnbindButton.setEnabled(self.target.currentText() != self.source.currentText()))
        
        self.rkeyLabel = QLabel("Routing Key:")
        self.rkey = QLineEdit()

        self.addBindButton = QPushButton("Bind")
        self.addBindButton.setObjectName('addBind')
        self.addBindButton.setEnabled(False)
        self.addBindButton.clicked.connect(self.buttonClicked)
               
        self.addUnbindButton = QPushButton("UnBind")
        self.addUnbindButton.setObjectName('unBind')
        self.addUnbindButton.setEnabled(False)
        self.addUnbindButton.clicked.connect(self.buttonClicked)

        self.bindingArgsGroupBox = QGroupBox("Arguments")

        vboxbindingargstable = QVBoxLayout()

        hboxbuttonbindingargs = QHBoxLayout()        

        self.bindingArgsAddButton = QPushButton("")
        self.bindingArgsDelButton = QPushButton("")

        self.bindingArgsAddButton.setIcon(QIcon(__IMAGES_PATH__ + '/addrow.png'))
        self.bindingArgsAddButton.setIconSize(QSize(25,25))

        self.bindingArgsDelButton.setIcon(QIcon(__IMAGES_PATH__ + '/deleterow.png'))
        self.bindingArgsDelButton.setIconSize(QSize(25,25))

        self.bindingArgsAddButton.setObjectName('addBindArgsKey')
        self.bindingArgsDelButton.setObjectName('delBindArgsKey')
        self.bindingArgsDelButton.setEnabled(False)
        
        self.bindingArgsAddButton.clicked.connect(self.buttonClicked)
        self.bindingArgsDelButton.clicked.connect(self.buttonClicked)

        hboxbuttonbindingargs.addWidget(QLabel("      "))
        hboxbuttonbindingargs.addWidget(QLabel("      "))
        hboxbuttonbindingargs.addWidget(QLabel("      "))
        hboxbuttonbindingargs.addWidget(QLabel("      "))
        hboxbuttonbindingargs.addWidget(self.bindingArgsAddButton)
        hboxbuttonbindingargs.addWidget(self.bindingArgsDelButton)

        headers = ["Key", "Value"]       
        datainbinding = []

        self.bindingargstablemodel = TableModel(datainbinding, headers, self)
        self.bindingargstablemodelview = QTableView()  
        self.bindingargstablemodelview.setSelectionMode(QAbstractItemView.SingleSelection)   

        self.bindingargstablemodelview.clicked.connect(self.showTableSelectedRowColumn)

        self.set_table_view_attributes(self.bindingargstablemodelview, self.bindingargstablemodel, datainbinding)        
        
        self.bindingArgsGroupBox.setLayout(vboxbindingargstable)

        vboxbindingargstable.addLayout(hboxbuttonbindingargs)
        vboxbindingargstable.addWidget(self.bindingargstablemodelview)        

        layoutBinding.addRow(self.exchange2queue, self.exchange2exchange)
        layoutBinding.addRow(self.sourceLabel, self.source)
        layoutBinding.addRow(self.targetLabel, self.target)
        layoutBinding.addRow(self.rkeyLabel, self.rkey)
        layoutBinding.addRow(self.bindingArgsGroupBox)

        bindbuttonlayout = QHBoxLayout()
        bindbuttonlayout.addWidget(self.addBindButton)
        bindbuttonlayout.addWidget(self.addUnbindButton)

        layoutBinding.addRow(bindbuttonlayout)        
                
        self.bindinggroupBox.setLayout(layoutBinding)

        hboxEQB2.addWidget(self.bindinggroupBox)

        vBoxEQB.addLayout(hboxEQB1)
        vBoxEQB.addLayout(hboxEQB2)        
    
        self.widget.setLayout(vBoxEQB)
        
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

    def showTableSelectedRowColumn(self, index):
        if self.exchangeadd:
            self.exArgsDelButton.setEnabled(True)

        if self.queueadd:
            self.qArgsDelButton.setEnabled(True)

        if self.bindadd:
            self.bindingArgsDelButton.setEnabled(True)

        self.tableSelectedRow = index.row()
        self.tableSelectedColumn = index.column()

    def btnstate(self,b):	
      if b.text() == "Exchange to Queue":
         if b.isChecked() == True:
           self.target.clear()
           for item in self.qlist:                
                name = item["name"]
                if len(name) == 0 or name.find(self._userId.lower().replace("_","")) > -1:
                    if(len(name) != 0):
                        self.target.addItem(str(name))                
				
      if b.text() == "Exchange to Exchange":
         if b.isChecked() == True:
            self.target.clear()            
            for item in self.elist:
                    name = item["name"]
                    if len(name) == 0 or name.find(self._userId.lower().replace("_","")) > -1:
                        if(len(name) != 0):                            
                            self.target.addItem(str(name))         
            

    def buttonClicked(self):
        button = self.sender()
        #print(button.objectName())
        
        if not button: return  

        buttonObjectName = button.objectName()

        exTableModel = self.exargstablemodelview.model()
        qTableModel = self.qargstablemodelview.model()
        bindingTableModel = self.bindingargstablemodelview.model()

        if buttonObjectName == "addExArgsKey":
            data = [[]]
            self.addRow(exTableModel, data)
            self.exchangeadd = True
        elif buttonObjectName == "delExArgsKey":
            del exTableModel.arraydata[self.tableSelectedRow]
            exTableModel.changeData(exTableModel.arraydata)
           
            self.exArgsDelButton.setEnabled(False)
        elif buttonObjectName == "addQArgsKey":
            data1 = [[]]
            self.addRow(qTableModel, data1)
            self.queueadd = True
        elif buttonObjectName == "delQArgsKey": 
            del qTableModel.arraydata[self.tableSelectedRow]
            qTableModel.changeData(qTableModel.arraydata)
           
            self.qArgsDelButton.setEnabled(False)
        elif buttonObjectName == "addBindArgsKey":
            data2 = [[]]
            self.addRow(bindingTableModel, data2)
            self.bindadd = True
        elif buttonObjectName == "delBindArgsKey": 
            del bindingTableModel.arraydata[self.tableSelectedRow]
            bindingTableModel.changeData(bindingTableModel.arraydata)
           
            self.bindingArgsDelButton.setEnabled(False)
        elif buttonObjectName == "addExchange":
            #exchange_declare(exchange, exchange_type='direct', passive=False, durable=False, auto_delete=False, internal=False, arguments=None, callback=None)            

            exchange = self.exName.text()
            exchange_type = str(self.exType.currentText())
            durable = True if str(self.durability.currentText()) == "Durable" else False
            auto_delete = False if str(self.autoDelete.currentText()) == "No" else True
            internal = False if str(self.internal.currentText()) == "No" else True

            exTableModel.removeRowsWithEmptyColumns()
            arguments = dict(exTableModel.arraydata)
            if arguments == {}:
                    arguments = None

            #print(exchange, exchange_type, durable, auto_delete, internal, arguments)
            try:
                channel = self.eqbConnection.channel()                
                channel.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=durable, auto_delete=auto_delete, internal=internal, arguments=arguments)
                if channel.is_open:
                    channel.close()
                
                MessageBox.message(QMessageBox.Information, "RabbitMQ Exchange", "Exchange Created!", "{exch} has been created.".format(exch=exchange))

                self.elist = RestFunctions.exchange_list(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)
                
                for item in self.elist:
                    name = item["name"]
                    if len(name) == 0 or name.find(self._userId.lower().replace("_","")) > -1:
                        if(len(name) != 0):
                            self.source.addItem(str(name)) 
                self._refresh.emit(True)                
            except Exception as e:
                error = str(e).strip().replace("(", "").replace(")", "").split(",")
                textandinfo = error[1].replace("\"","").split("-")
                text = textandinfo[0].replace("\"","").strip()
                infoText = textandinfo[1].replace("\"","").strip()  + ". Check Queue naming policy with your administrator."    
                MessageBox.message(QMessageBox.Critical, "RabbitMQ Exchange Creation - Error ({})".format(error[0]), text, infoText)      
                
        elif buttonObjectName == "delExchange":
            #exchange_delete(exchange=None, if_unused=False, callback=None)
            try:
                channel = self.eqbConnection.channel()

                exchange = self.exName.text()
                exch_exist = channel.exchange_declare(exchange=exchange, passive=True)

                if exch_exist:
                    channel.exchange_delete(exchange=exchange)

                    MessageBox.message(QMessageBox.Information, "RabbitMQ Exchange", "Exchange Deleted!", "{exch} has been deleted.".format(exch=exchange))

                    self.elist = RestFunctions.exchange_list(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)
                    
                    for item in self.elist:
                        name = item["name"]
                        if len(name) == 0 or name.find(self._userId.lower().replace("_","")) > -1:
                            if(len(name) != 0):
                                self.source.addItem(str(name))          
                    self._refresh.emit(True)    

                if channel.is_open:
                    channel.close()                
                           
            except Exception as e:
                error = str(e).strip().replace("(", "").replace(")", "").split(",")
                textandinfo = error[1].replace("\"","").split("-")
                text = textandinfo[0].replace("\"","").strip()
                infoText = textandinfo[1].replace("\"","").strip()
                MessageBox.message(QMessageBox.Critical, "RabbitMQ Exchange Deletion - Error ({})".format(error[0]), text, infoText)    
        elif buttonObjectName == "addQueue":
            queue = self.qName.text()
            durable = True if str(self.qDurability.currentText()) == "Durable" else False
            auto_delete = False if str(self.qAutoDelete.currentText()) == "No" else True
            
            qTableModel.removeRowsWithEmptyColumns()
            arguments = dict(qTableModel.arraydata)
            
            if arguments == {}:
                arguments = None

            try:
                channel = self.eqbConnection.channel()
                
                channel.queue_declare(queue=queue, durable=durable, auto_delete=auto_delete, arguments=arguments)
                if channel.is_open:
                    channel.close()

                MessageBox.message(QMessageBox.Information, "RabbitMQ Queue", "Queue Created!", "{que} has been added.".format(que=queue))

                self.qlist = RestFunctions.queue_list(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)
                for item in self.qlist:                
                    name = item["name"]
                    if len(name) == 0 or name.find(self._userId.lower().replace("_","")) > -1:
                        if(len(name) != 0):
                            self.target.addItem(str(name)) 
                self._refresh.emit(True)    
            except Exception as e:
                error = str(e).strip().replace("(", "").replace(")", "").split(",")
                textandinfo = error[1].replace("\"","").split("-")
                text = textandinfo[0].replace("\"","").strip()
                infoText = textandinfo[1].replace("\"","").strip()  + ". Check Queue naming policy with your administrator."    
                MessageBox.message(QMessageBox.Critical, "RabbitMQ Queue Creation - Error ({})".format(error[0]), text, infoText)
            
        elif buttonObjectName == "delQueue":
            try:
                channel = self.eqbConnection.channel()
                queue = self.qName.text()

                queue_exist = channel.queue_declare(queue=queue, passive=True)

                if queue_exist:
                    channel.queue_delete(queue=queue)

                    MessageBox.message(QMessageBox.Information, "RabbitMQ Queue", "Queue Deleted!", "{que} has been deleted.".format(que=queue))
                    
                    self.qlist = RestFunctions.queue_list(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)
                    for item in self.qlist:                
                        name = item["name"]
                        if len(name) == 0 or name.find(self._userId.lower().replace("_","")) > -1:
                            if(len(name) != 0):
                                self.target.addItem(str(name))
                    self._refresh.emit(True)                

                if channel.is_open:
                    channel.close()
                  
            except Exception as e:
                error = str(e).strip().replace("(", "").replace(")", "").split(",")
                textandinfo = error[1].replace("\"","").split("-")
                text = textandinfo[0].replace("\"","").strip()
                infoText = textandinfo[1].replace("\"","").strip()
                MessageBox.message(QMessageBox.Critical, "RabbitMQ Queue Deletion - Error ({})".format(error[0]), text, infoText)
            self._refresh.emit(True)       
        elif buttonObjectName == "purgeQueue":
            try:
                channel = self.eqbConnection.channel()
                queue = self.qName.text()           

                queue_exist = channel.queue_declare(queue=queue, passive=True)

                if queue_exist: 
                    channel.queue_purge(queue=queue)

                    MessageBox.message(QMessageBox.Information, "RabbitMQ Queue", "Queue Purged!", "{que} has been purged.".format(que=queue))

                    self._refresh.emit(True)    
                if channel.is_open:
                    channel.close() 
            except Exception as e:
                error = str(e).strip().replace("(", "").replace(")", "").split(",")
                textandinfo = error[1].replace("\"","").split("-")
                text = textandinfo[0].replace("\"","").strip()
                infoText = textandinfo[1].replace("\"","").strip()
                MessageBox.message(QMessageBox.Critical, "RabbitMQ Queue Purge - Error ({})".format(error[0]), text, infoText)  
            
        elif buttonObjectName == "addBind":            

            destination = self.target.currentText()
            source = self.source.currentText()
            routing_key = self.rkey.text()

            bindingTableModel.removeRowsWithEmptyColumns()
            arguments = dict(bindingTableModel.arraydata)
            if arguments == {}:
                    arguments = None 
            
            if self.exchange2exchange.isChecked():

                if len(routing_key) == 0:
                    routing_key = ''               

                channel = self.eqbConnection.channel()
                channel.exchange_bind(destination=destination, source=source, routing_key=routing_key, arguments=arguments)                
                MessageBox.message(QMessageBox.Information, "RabbitMQ Binding", "Exchange to Exchange Binding!", 
                                               "Binding created between Exchange:{exch1} and Exchange:{exch2}.".format(exch1=destination, exch2=source))

                self._refresh.emit(True)    

                if channel.is_open:
                    channel.close()
            elif self.exchange2queue.isChecked():
                if len(routing_key) == 0:
                    routing_key = None

                channel = self.eqbConnection.channel()
                channel.queue_bind(queue=destination, exchange=source, routing_key=routing_key, arguments=arguments)
                MessageBox.message(QMessageBox.Information, "RabbitMQ Binding", "Queue to Exchange Binding!", 
                                               "Binding created between Queue:{que} and Exchange:{exch1}.".format(que=destination, exch1=source))
                self._refresh.emit(True)    
                if channel.is_open:
                    channel.close()
            
        elif buttonObjectName == "unBind":           

            destination = self.target.currentText()
            source = self.source.currentText()
            routing_key = self.rkey.text()

            bindingTableModel.removeRowsWithEmptyColumns()
            arguments = dict(bindingTableModel.arraydata)
            if arguments == {}:
                arguments = None 

            if self.exchange2exchange.isChecked():
                
                if len(routing_key) == 0:
                    routing_key = ''

                channel = self.eqbConnection.channel()
                channel.exchange_unbind(destination=destination, source=source, routing_key=routing_key, arguments=arguments)              
                MessageBox.message(QMessageBox.Information, "RabbitMQ UnBinding", "Exchange to Exchange UnBinding!", 
                                               "Binding removed between Exchange:{exch1} and Exchange:{exch2}.".format(exch1=destination, exch2=source))

                self._refresh.emit(True)        
                if channel.is_open:
                    channel.close()
            elif self.exchange2queue.isChecked():                

                if len(routing_key) == 0:
                    routing_key = None

                channel = self.eqbConnection.channel()                
                channel.queue_unbind(queue=destination, exchange=source, routing_key=routing_key, arguments=arguments)                
                MessageBox.message(QMessageBox.Information, "RabbitMQ UnBinding", "Queue to Exchange UnBinding!", 
                                               "Binding removed between Queue:{que} and Exchange:{exch1}.".format(que=destination, exch1=source))
                self._refresh.emit(True)    
                if channel.is_open:
                    channel.close()    

            
              
    def addRow(self, table_model, data):
        rowcount = table_model.rowCount()
        if rowcount == 0:
            table_model.update(rowcount, data) 
        else:
            if len(table_model.arraydata[rowcount - 1][0]) != 0:
                table_model.update(rowcount, data) 

    def show_login(self):
        self.login.show()       
        self.loginmw.show()
        self.login.setReference(self.loginmw)


    def disconnect(self):
        self.reset()

        if self.session is not None:
            print("Closing Request Session - EQB")
            self.session.close()

        if self.login is not None:
            print("Closing Connection Information Dialog - EQB")
            self.login.close()

        if self.eqbConnection is not None and not self.fromParent:            
            print("Closing AMQP Connection - EQB")
            self.eqbConnection.close()
        else:    
            self.eqbConnection = None        

        self.connectAction.setEnabled(True)
        self.loginButton.setEnabled(True)
    
    def reset(self):
        self.evhost.clear()
        self.exName.setText("")
        self.exType.clear()

        self.qvhost.clear()        
        self.qName.setText("")
        
        #self.qNode.clear()

        self.source.clear()
        self.target.clear()
        self.rkey.setText("")         

        edata=[]
        self.exargstablemodelview.model().changeData(edata)

        qdata = []
        self.qargstablemodelview.model().changeData(qdata)

        adata = []
        self.bindingargstablemodelview.model().changeData(adata)

    def loginCancelled(self, cancelled):
        self._cancelled = cancelled
        #print(self._cancelled)

        if self._cancelled == False:
            self.session = requests.Session() 
            self.sessionAvailable = True 
            
            self.disconnect()

            self.populate()

            #print("self.eqbConnection = {}".format(self.eqbConnection))

            if self.eqbConnection is None:
                self.eqbConnection = RabbitMQPikaConnection.connect(RabbitMQPikaConnection, self, self._commandUrl, self._userId, self._password, self._certName, self._vhost, 'RabbitMQ_Util_EQB')  
            
            self.connectAction.setEnabled(True)
            self.loginButton.setEnabled(True)

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

    def getConnectionVhost(self, vhost):
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

    def refresh(self):
        self.reset()
        self.populate()

    def setConnection(self, connection, sessionAvailable, session, _webUrl, _userId, _password, _vhost, _certName, _frame):
        self.fromParent = True

        self.eqbConnection = connection

        #print("From rmq main - self.eqbConnection = {}".format(self.eqbConnection))

        self.sessionAvailable = sessionAvailable
        self.session = session
        self._webUrl = _webUrl
        self._userId = _userId
        self._password = _password
        self._vhost = _vhost
        self._certName = _certName

        self.frame = _frame

        self.reset()
        
        self.populate()

    def populate(self):

        eqvhost = RestFunctions.vhosts(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)
        for item in eqvhost:
            self.evhost.addItem(item[1])            
            self.qvhost.addItem(item[1])

        index = self.evhost.findText(self._vhost, Qt.MatchFixedString)
        if index >= 0:
            self.evhost.setCurrentIndex(index)    

        index = self.qvhost.findText(self._vhost, Qt.MatchFixedString)
        if index >= 0:
            self.qvhost.setCurrentIndex(index)        

        etypesAndNodes = RestFunctions.nodes(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)

        for item in etypesAndNodes:
            etype = item["exchange_types"]
            for elem in etype:
                name = elem["name"]
                if(name != "x-federation-upstream"):
                    self.exType.addItem(name) 

        self.elist = RestFunctions.exchange_list(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)
        self.qlist = RestFunctions.queue_list(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)

        for item in self.elist:
            name = item["name"]
            if len(name) == 0 or name.find(self._userId.lower().replace("_","")) > -1:
                if(len(name) != 0):
                    self.source.addItem(str(name)) 

        for item in self.qlist:                
            name = item["name"]
            if len(name) == 0 or name.find(self._userId.lower().replace("_","")) > -1:
                if(len(name) != 0):
                    self.target.addItem(str(name))    
    
    def closewin(self):
        if self is not None:
            self.close()

        if self.frame is not None:
            self.frame.close()

        self.login.close()
        self.loginmw.close()

        if self.eqbConnection is not None and self.eqbConnection.is_open:
            self.eqbConnection.close()

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

        if self.eqbConnection is not None and self.eqbConnection.is_open:
            self.eqbConnection.close()

        if self.session is not None:
            self.session.close()
    
        
        #self.qapp.exit()        
    