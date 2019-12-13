import sys
import requests

import os

import json

import decrypt

import styles
import windows

from configparser import ConfigParser

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QAction, QHBoxLayout, QVBoxLayout, QMainWindow, 
QWidget, QListWidget, QTableView, QAbstractItemView, QHeaderView, QLineEdit, QLabel, QGroupBox, QStatusBar, QDesktopWidget, QMessageBox)

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QFont

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize

from manage_ini import ConnectMenu
from exportMessages import ExportMessagesDialog
from rmqmodel import TableModel
from restFunctions import RestFunctions
from connectAmqp import RabbitMQPikaConnection
from importMessages import ImportMessages
from shovel_messages import ShovelMenu
from encrypt_string import EncryptDialog
from decrypt_string import DecryptDialog
from deleteMessages import DeleteMessages
from exchange_queues_bindings import ExchangeQueuesBindingsMenu
from extract_config import ExtractConfigMenu
from importConfig import ImportConfig
from mendConfig import MendConfig


__RESOURCES_PATH__ = "./resources"
__IMAGES_PATH__ = __RESOURCES_PATH__ + "/images"

	
class RMQUMenu(QtWidgets.QMainWindow):
    
    _mainExited = QtCore.pyqtSignal(bool)

    def __init__(self, parser):
        
        super(RMQUMenu, self).__init__()

        self.setWindowTitle("RabbitMQ Utility")    # Set the window title

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

        self.connection = None

        self.exportMessage = {}

        self.otherMessage = {}

        self.queue_name = ""

        self.eitems = None
        self.qitems = None

        self.frame = None

        self.parser = parser

        #------------------------------ 
        self.qapp = QApplication([])
        #V = self.qapp.desktop().screenGeometry()
        #h = V.height() - 600 
        #w = V.width() - 600

        h = 800 
        w = 1100

        self.resize(w, h)

        self.widget = QWidget()        

        self.shovelMenu = ShovelMenu(self.parser, __RESOURCES_PATH__)
        self.shovelMenu._refresh.connect(self.refresh)
        self.shovelmw = windows.ModernWindow(self.shovelMenu, self.parser)
        
        self.exqbindingMenu = ExchangeQueuesBindingsMenu(self.parser, __RESOURCES_PATH__)
        self.exqbindingMenu._refresh.connect(self.refresh)
        self.eqbmw = windows.ModernWindow(self.exqbindingMenu, self.parser)

        self.exportMessagesDialog = ExportMessagesDialog(__IMAGES_PATH__)
        self.exportMessagesDialog._fileName.connect(self.getExportFileName)
        self.expmsgmw = windows.ModernWindow(self.exportMessagesDialog, self.parser)

        #self.login = LoginDialog(self.parser)
        self.login = ConnectMenu(self.parser, __RESOURCES_PATH__)
        
        self.login._cancelled.connect(self.loginCancelled)

        self.login._webUrl.connect(self.getWebConnectionUrl)
        self.login._commandUrl.connect(self.getCommandConnectionUrl)
        self.login._userId.connect(self.getConnectionUser)
        self.login._password.connect(self.getConnectionPassword)
        self.login._vhost.connect(self.getCconnectionVhost)
        self.login._certName.connect(self.getConnectionCertName)
        self.login._certPass.connect(self.getConnectionCertPass)
        self.loginmw = windows.ModernWindow(self.login, self.parser)

        self.encPass = EncryptDialog(__IMAGES_PATH__)
        self.epassmw = windows.ModernWindow(self.encPass, self.parser)

        self.decPass = DecryptDialog(__IMAGES_PATH__)
        self.dpassmw = windows.ModernWindow(self.decPass, self.parser)

        self.extactConfig = ExtractConfigMenu(__IMAGES_PATH__, self.parser) 
        self.extconfmw = windows.ModernWindow(self.extactConfig, self.parser)

        self.patchRConfig = MendConfig(__IMAGES_PATH__, self.parser) 
        self.patconfmw = windows.ModernWindow(self.patchRConfig, self.parser)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        #----------------------------------------- MENU BAR -------------------------------------------------
        # Create Connect
        self.connectAction = QAction(QIcon(__IMAGES_PATH__ + '/connect.png'), '&Connect', self)        
        self.connectAction.setShortcut('SHIFT+C')
        self.connectAction.setStatusTip('Connect')
        self.connectAction.triggered.connect(self.get_login)

        # Create refresh
        self.refreshAction = QAction(QIcon(__IMAGES_PATH__ + '/refresh.png'), '&Refresh', self)        
        self.refreshAction.setShortcut('CTRL+R')
        self.refreshAction.setStatusTip('Refresh')
        self.refreshAction.triggered.connect(self.refresh)

        # Create Disconnect
        self.disconnectAction = QAction(QIcon(__IMAGES_PATH__ + '/disconnect.png'), '&DisConnect', self)        
        self.disconnectAction.setShortcut('SHIFT+D')
        self.disconnectAction.setStatusTip('Disconnect')
        self.disconnectAction.triggered.connect(self.disconnect)
        
        # Create Exit action
        self.exitAction = QAction(QIcon(__IMAGES_PATH__ + '/terminate.png'), '&Exit', self)        
        self.exitAction.setShortcut('ALT+F4')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.closewin)

        # Create Import
        self.importAction = QAction(QIcon(__IMAGES_PATH__ + '/import_messages.png'), '&Import Message(s)', self)        
        self.importAction.setShortcut('ALT+I')
        self.importAction.setStatusTip('Import')
        self.importAction.triggered.connect(lambda: ImportMessages.importMessages(ImportMessages, self, self.sessionAvailable, self.connection))

        # Create Export
        self.exportAction = QAction(QIcon(__IMAGES_PATH__ + '/export_messages.png'), '&Export Message(s)', self)        
        self.exportAction.setShortcut('ALT+E')
        self.exportAction.setStatusTip('Export')
        self.exportAction.triggered.connect(self.exportMessages)

        # Create Shovel
        self.shovelAction = QAction(QIcon(__IMAGES_PATH__ + '/shovel_messages.png'), '&Shovel Message(s)', self)        
        self.shovelAction.setShortcut('ALT+S')
        self.shovelAction.setStatusTip('Shovel')
        self.shovelAction.triggered.connect(self.shovelMessages)

        # Create Delete
        self.deleteAction = QAction(QIcon(__IMAGES_PATH__ + '/delete_messages.png'), 'De&lete', self)        
        self.deleteAction.setShortcut('ALT+X')
        self.deleteAction.setStatusTip('Delete')
        self.deleteAction.triggered.connect(self.deleteMessages)

        # Create Encrypt
        self.encAction = QAction(QIcon(__IMAGES_PATH__ + '/encrypt.png'), 'E&nrypt String', self)        
        self.encAction.setShortcut('Ctrl+E')
        self.encAction.setStatusTip('Encrypt')
        self.encAction.triggered.connect(self.encryptString)

        # Create Decrypt
        self.decAction = QAction(QIcon(__IMAGES_PATH__ + '/decrypt.png'), 'Dec&rypt String', self)        
        self.decAction.setShortcut('Ctrl+D')
        self.decAction.setStatusTip('Decrypt')
        self.decAction.triggered.connect(self.decryptString)

        # Extract Config to file
        self.extConfAction = QAction(QIcon(__IMAGES_PATH__ + '/export_config.png'), 'Export Resources', self)        
        self.extConfAction.setShortcut('Ctrl+X')
        self.extConfAction.setStatusTip('Export Exchanges, Queues and Bindings to File')
        self.extConfAction.triggered.connect(self.extractConfigAction)

        # Import Config to file
        self.impConfAction = QAction(QIcon(__IMAGES_PATH__ + '/import_config.png'), 'Import Resources', self)        
        self.impConfAction.setShortcut('Ctrl+I')
        self.impConfAction.setStatusTip('Import Exchanges, Queues and Bindings from File')
        self.impConfAction.triggered.connect(lambda: ImportConfig.importConfig(ImportConfig, self, self.sessionAvailable, self.connection, self.e_items, self.q_items))
        
        # Patch Config to file
        self.patchConfAction = QAction(QIcon(__IMAGES_PATH__ + '/patch_config.png'), 'Patch Resources', self)        
        self.patchConfAction.setShortcut('Ctrl+P')
        self.patchConfAction.setStatusTip('Patch Exchanges, Queues and Bindings from File')
        self.patchConfAction.triggered.connect(self.patchConfig)

        # Create Exchange/Queue binding        
        self.exQBindingAction = QAction(QIcon(__IMAGES_PATH__ + '/eqb.png'),'&Add Resources Manually', self)        
        self.exQBindingAction.setShortcut('SHIFT+M')
        self.exQBindingAction.setStatusTip('Add Exchanges, Queues and Bindings Manually')
        self.exQBindingAction.triggered.connect(self.exchangeQueueBindingAction)

        menuBar = self.menuBar()
        
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.connectAction)
        fileMenu.addAction(self.refreshAction)
        fileMenu.addAction(self.disconnectAction)
        fileMenu.addAction(self.exitAction)

        messageMenu = menuBar.addMenu('&Messages')
        messageMenu.addAction(self.importAction)
        messageMenu.addAction(self.exportAction)
        messageMenu.addAction(self.shovelAction)
        messageMenu.addAction(self.deleteAction)

        utilsMenu = menuBar.addMenu('&Admin')
        utilsMenu.addAction(self.encAction)
        utilsMenu.addAction(self.decAction)
        
        confMenu = menuBar.addMenu('&Configuration')
        confMenu.addAction(self.extConfAction)
        confMenu.addAction(self.impConfAction)
        confMenu.addAction(self.patchConfAction)
        confMenu.addAction(self.exQBindingAction)

        #----------------------------------------- TOOL BAR -------------------------------------------------

        self.toolbar = self.addToolBar('')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)

        #self.toolbar.setIconSize(QSize(50,50))
        #self.toolbar.setGeometry(100, 100, 400, 400)

        #------------ Connect -------------
        self.loginButton = QAction(QIcon(__IMAGES_PATH__ + '/connect.png'), '&Connect', self)
        self.loginButton.setIconText('Connect')
        self.loginButton.setStatusTip("Click here to login")
        self.loginButton.triggered.connect(self.get_login)
        self.toolbar.addAction(self.loginButton)

        #------------ Refresh -------------
        self.refreshButton = QAction(QIcon(__IMAGES_PATH__ + '/refresh.png'), '&Refresh', self)
        self.refreshButton.triggered.connect(self.refresh)
        self.refreshButton.setStatusTip("Click here to refresh data")
        self.toolbar.addAction(self.refreshButton)         

        self.toolbar.addSeparator()

        #------------ Import -------------
        self.importMessagesButton = QAction(QIcon(__IMAGES_PATH__ + '/import_messages.png'), 'Import Messages', self)
        self.importMessagesButton.triggered.connect(lambda: ImportMessages.importMessages(ImportMessages, self, self.sessionAvailable, self.connection))        
        self.importMessagesButton.setStatusTip("Click here to import message(s) from json file") 
        self.toolbar.addAction(self.importMessagesButton)        
        
        
        #------------ Export -------------
        self.exportMessagesButton = QAction(QIcon(__IMAGES_PATH__ + '/export_messages.png'), 'Export Messages', self)
        self.exportMessagesButton.triggered.connect(self.exportMessages)
        self.exportMessagesButton.setStatusTip("Click here to export message(s) to json file") 
        self.toolbar.addAction(self.exportMessagesButton)   

        #------------ Shovel Message -------------
        self.shovelMessagesButton = QAction(QIcon(__IMAGES_PATH__ + '/shovel_messages.png'), 'Shovel Messages', self)
        self.shovelMessagesButton.triggered.connect(self.shovelMessages)        
        self.shovelMessagesButton.setStatusTip("Click here to copy message(s) to another queue on same or other server") 
        self.toolbar.addAction(self.shovelMessagesButton)    

        #------------ Delete Message -------------
        self.deleteMessagesButton = QAction(QIcon(__IMAGES_PATH__ + '/delete_messages.png'), 'Delete Messages', self)
        self.deleteMessagesButton.triggered.connect(self.deleteMessages)   
        self.deleteMessagesButton.setStatusTip("Click here to delete selected message(s)")      
        self.toolbar.addAction(self.deleteMessagesButton)    

        self.toolbar.addSeparator()
        
        # Extract Config to file
        self.extConfButton = QAction(QIcon(__IMAGES_PATH__ + '/export_config.png'), 'Export Resources', self)        
        self.extConfButton.setStatusTip('Export Resources to file')
        self.extConfButton.triggered.connect(self.extractConfigAction)
        self.toolbar.addAction(self.extConfButton)    

        # Import Config to file
        self.impConfButton = QAction(QIcon(__IMAGES_PATH__ + '/import_config.png'), 'Import Resources', self)        
        self.impConfButton.setStatusTip('Import Resources from file')
        self.impConfButton.triggered.connect(lambda: ImportConfig.importConfig(ImportConfig, self, self.sessionAvailable, self.connection, self.e_items, self.q_items))
        self.toolbar.addAction(self.impConfButton)    

        # Patch Config to file
        self.patchConfButton = QAction(QIcon(__IMAGES_PATH__ + '/patch_config.png'), 'Patch Resources', self)        
        self.patchConfButton.setStatusTip('Patch Resources in file')
        self.patchConfButton.triggered.connect(self.patchConfig)
        self.toolbar.addAction(self.patchConfButton)    

        # Create Exchange/Queue binding        
        self.exQBindingButton = QAction(QIcon(__IMAGES_PATH__ + '/eqb.png'),'&Add Resources Manually', self)        
        self.exQBindingButton.setStatusTip('Add Resources Manually')
        self.exQBindingButton.triggered.connect(self.exchangeQueueBindingAction)
        self.toolbar.addAction(self.exQBindingButton)    

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

        #self.toolbar.setIconSize(QSize(32,32))
        #self.toolbar.setGeometry(100, 100, 400, 400)

        # --- set button enabled to false
        self.exportMessagesButton.setEnabled(False)      
        self.importMessagesButton.setEnabled(False)   
        self.disconnectButton.setEnabled(False)
        self.shovelMessagesButton.setEnabled(False)   
        self.deleteMessagesButton.setEnabled(False)           
        self.refreshButton.setEnabled(False) 
        self.extConfButton.setEnabled(False) 
        self.impConfButton.setEnabled(False) 
        self.patchConfButton.setEnabled(False)
        self.exQBindingButton.setEnabled(False) 

        #-- Set menu bar items to false
        self.exportAction.setEnabled(False)      
        self.importAction.setEnabled(False)  
        self.refreshAction.setEnabled(False) 
        self.disconnectAction.setEnabled(False)
        self.shovelAction.setEnabled(False)   
        self.deleteAction.setEnabled(False)  
        self.exQBindingAction.setEnabled(False) 
        self.extConfAction.setEnabled(False)
        self.impConfAction.setEnabled(False)
        #self.patchConfAction.setEnabled(False)

        self.eGroupBox = QGroupBox("Exchanges")
        self.exchange_list = QListWidget()
        self.exchange_list.itemSelectionChanged.connect(lambda: RestFunctions.selectedExchangeList(RestFunctions, self, self.session, self._webUrl, self.exchange_list.currentItem().text(), self._userId, self._password, self._certName))
        #self.exchange_list.itemClicked.connect(lambda: RestFunctions.selectedExchangeList(RestFunctions, self, self.session, self._webUrl, self.exchange_list.currentItem().text(), self._userId, self._password, self._certName))
        
        self.qGroupBox = QGroupBox("Queues")
        self.queue_list = QListWidget()
        
        self.queue_list.itemSelectionChanged.connect(lambda: RestFunctions.selectedQueueList(RestFunctions, self, self.session, self._webUrl, self.queue_list.currentItem().text(), self._userId, self._password, self._certName))
        #self.queue_list.itemClicked.connect(lambda: RestFunctions.selectedQueueList(RestFunctions, self, self.session, self._webUrl, self.queue_list.currentItem().text(), self._userId, self._password, self._certName))
        
        self.eqBindingsGroupBox = QGroupBox("Exchange - Queues binding")      

        headers = ["Id", "Source", "Exchange Type", "Auto Delete Exchange?", "Destination", "Destination Type", "Routing Key", "Arguments", "Properties Key"]       
        datain = []
        self.bindingTableSelectedRow = 0
        self.messagingTableSelectedRow = 0

        self.bindingtablemodel = TableModel(datain, headers, self)
        self.bindingtablemodelview = QTableView()  
        self.bindingtablemodelview.setSelectionMode(QAbstractItemView.SingleSelection)   
        
        self.set_table_view_attributes(self.bindingtablemodelview, self.bindingtablemodel, False, datain)        

        self.bindingtablemodelview.clicked.connect(self.showBindingTableSelectedRowContent)        
        self.bindingtablemodelview.clicked.connect(lambda: self.bindingTableClick(self.bindingtablemodel))       
       
        self.qMessagessGroupBox = QGroupBox("Queue Messages")

        message_header = ["Id", "Exchange", "Routing Key", "Payload Bytes", "Redelivered",  "Properties", "Headers", "Payload"]
        messageData = []
        self.messagetablemodel = TableModel(messageData, message_header, self)
        self.messagetablemodelview = QTableView()            
        self.messagetablemodelview.setSelectionMode(QAbstractItemView.MultiSelection)
      
        self.set_table_view_attributes(self.messagetablemodelview, self.messagetablemodel, True, messageData)        

        self.messagetablemodelview.clicked.connect(self.showMessagingTableSelectedRowContent)                       
        self.messagetablemodelview.selectionModel().selectionChanged.connect(lambda: self.change_display_result(self.messagetablemodelview))       

        #----------- Top UI ------------------
        hbox = QHBoxLayout()

        eqvLayout = QVBoxLayout()
        
        #------------------ Exchange List ----------------------------------------
        vboxexsub = QVBoxLayout()
        
        hboxexsub = QHBoxLayout()

        self.exlistsearch = QLineEdit()
        self.exlistsearch.textEdited.connect(lambda: self.searchItem(self.exchange_list, self.exlistsearch.text(), self.e_items))
        self.exlistsearch.returnPressed.connect(lambda: self.searchItem(self.exchange_list, self.exlistsearch.text(), self.e_items))
        
        hboxexsub.addWidget(QLabel("Search Exchange(s):"))
        hboxexsub.addWidget(self.exlistsearch) 
        
        vboxexsub.addLayout(hboxexsub) 
        vboxexsub.addWidget(self.exchange_list) 
        
        self.eGroupBox.setLayout(vboxexsub)

        #------------------ Queue List ----------------------------------------
        
        vboxqsub = QVBoxLayout()

        hboxqsub = QHBoxLayout()

        self.qlistsearch = QLineEdit()
        self.qlistsearch.textEdited.connect(lambda: self.searchItem(self.queue_list, self.qlistsearch.text(), self.q_items))
        self.qlistsearch.returnPressed.connect(lambda: self.searchItem(self.queue_list, self.qlistsearch.text(), self.q_items))
        
        hboxqsub.addWidget(QLabel("Search Queue(s):"))
        hboxqsub.addWidget(self.qlistsearch) 
        
        vboxqsub.addLayout(hboxqsub) 
        vboxqsub.addWidget(self.queue_list) 

        self.qGroupBox.setLayout(vboxqsub)

        hbox.addWidget(self.eGroupBox)
        hbox.addWidget(self.qGroupBox)

        #------------- Center UI ---------------
        hbox1 = QHBoxLayout()
        self.searchExchangeOrQueue=QLineEdit()
        
        vboxEQ = QVBoxLayout()
        hSearchLayout = QHBoxLayout()
        hSearchLayout.addWidget(QLabel("Search Binding(s):"))
        hSearchLayout.addWidget(self.searchExchangeOrQueue)
        hSearchLayout.addWidget(QLabel("# of Records:"))
        self.numEQRecs = QLineEdit()
        self.numEQRecs.setEnabled(False)
        hSearchLayout.addWidget(self.numEQRecs)
        vboxEQ.addLayout(hSearchLayout)
        vboxEQ.addWidget(self.bindingtablemodelview)
        
        #hbox1.addLayout(vboxEQ)

        self.eqBindingsGroupBox.setLayout(vboxEQ)

        hbox1.addWidget(self.eqBindingsGroupBox)

        self.searchExchangeOrQueue.textEdited.connect(lambda: self.searchLineEditied (self.bindingtablemodel, self.searchExchangeOrQueue, self.numEQRecs))
        self.searchExchangeOrQueue.returnPressed.connect(lambda: self.searchLineEditied (self.bindingtablemodel, self.searchExchangeOrQueue, self.numEQRecs))

        #------------- Bottom UI --------------------------
        hbox2 = QHBoxLayout()
        self.searchMessage=QLineEdit()
        
        vboxMsg = QVBoxLayout()             
        hQSearchLayout = QHBoxLayout()
        hQSearchLayout.addWidget(QLabel("Search Message(s):"))
        hQSearchLayout.addWidget(self.searchMessage)
        hQSearchLayout.addWidget(QLabel("# of Records:"))
        self.numMsgRecs = QLineEdit()
        self.numMsgRecs.setEnabled(False)
        hQSearchLayout.addWidget(self.numMsgRecs)
        vboxMsg.addLayout(hQSearchLayout)
        vboxMsg.addWidget(self.messagetablemodelview)
        
        self.searchMessage.textEdited.connect(lambda: self.searchLineEditied (self.messagetablemodel, self.searchMessage, self.numMsgRecs))
        self.searchMessage.returnPressed.connect(lambda: self.searchLineEditied (self.messagetablemodel, self.searchMessage, self.numMsgRecs))

        self.qMessagessGroupBox.setLayout(vboxMsg)

        #hbox2.addLayout(vboxMsg)
        hbox2.addWidget(self.qMessagessGroupBox)
        
        vbox = QVBoxLayout()
        
        vbox.addLayout(hbox)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        self.widget.setLayout(vbox)

        self.setCentralWidget(self.widget)     

    def searchItem(self, listWidgetName, search_string, eqitems):
        
        items = [item for item in eqitems if search_string in item] 
        
        if len(items) > 0:
            listWidgetName.clear()
            listWidgetName.addItems(items)
        else:
            #listWidgetName.setSelectionMode(QAbstractItemView.SingleSelection)    
            listWidgetName.clear()   
            for item in eqitems:  
                listWidgetName.addItem(str(item))
    

    def searchLineEditied(self, tableModel, searchText, recordCount):      
        rows = tableModel.rowCount()
        if rows:
            tableModel.setFilter(searchText.text())
            recordCount.setText(str(rows))               

    def bindingTableClick(self, table_model):

        binselectedData = table_model.arraydata[self.bindingTableSelectedRow]
        self.queue_name = binselectedData[4]

        data = RestFunctions.queue_messages(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self.queue_name, self._userId, self._password, self._certName)               

        dummyData = []
        self.messagetablemodelview.model().changeData(dummyData)

        self.messagetablemodelview.model().changeData(data)    
        
        self.messagetablemodelview.model().backupData()

        self.numMsgRecs.setText(str(self.messagetablemodelview.model().rowCount())) 

    #Gets a selected row  
    def showBindingTableSelectedRowContent(self, index):
        #print("current row is %d", index.row())
        self.bindingTableSelectedRow = index.row()        

    def showMessagingTableSelectedRowContent(self, index):
        #print("current row is %d", index.row())
        self.messagingTableSelectedRow = index.row()        

    def change_display_result(self, table_view):
        temp_entity = table_view.selectionModel().model()

        # Get rows that are selected
        rows=[idx.row() for idx in table_view.selectionModel().selectedRows()]        
        #print(rows, len(rows))   # or return rows

        # Get rows that are unselected
        rem_rows=[idx[0] - 1 for idx in table_view.model().arraydata if idx[0] - 1 not in rows]
        #print(rem_rows)

        if len(rows) > 0:
            self.exportMessagesButton.setEnabled(True)      
            self.shovelMessagesButton.setEnabled(True)   
            self.deleteMessagesButton.setEnabled(True)

            self.exportAction.setEnabled(True)      
            self.shovelAction.setEnabled(True)     
            self.deleteAction.setEnabled(True)     
        else:
            self.exportMessagesButton.setEnabled(False)      
            self.shovelMessagesButton.setEnabled(False)   
            self.deleteMessagesButton.setEnabled(False)

            self.exportAction.setEnabled(False)      
            self.shovelAction.setEnabled(False)     
            self.deleteAction.setEnabled(False)     

        self.exportMessage.clear()

        self.otherMessage.clear()
        
        for index in rows:
            self.messagingTableSelectedRow = index
            self.getmessagingTableData(temp_entity, self.exportMessage)          

        for index in rem_rows:
            self.messagingTableSelectedRow = index
            self.getmessagingTableData(temp_entity, self.otherMessage)        

    def getmessagingTableData(self, table_model, selectedRowOrOther):
        self.selectedData = table_model.arraydata[self.messagingTableSelectedRow]
        
        #print(self.selectedData)

        rowid = self.selectedData[0]
        exchange = self.selectedData[1]
        routingKey = self.selectedData[2]                
        message = self.selectedData[7].strip()              
        os.linesep.join(message.splitlines())

        props = self.selectedData[8]
        
        col = { 'exchange': exchange, 'routing_key': routingKey, 'body': message, 'properties': props }        

        key = 'message_{0}'.format(rowid)

        #print(key)
        if key not in selectedRowOrOther:
            selectedRowOrOther[key] = col    
        
        #print(selectedRowOrOther)
    

    def set_table_view_attributes(self, table_view, table_model, adjustRowHeight, data):     
        
        table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_view.setAlternatingRowColors(True)
        table_view.setModel(table_model)        
        table_view.setSortingEnabled(True)        
        
        # hide vertical header
        vh = table_view.verticalHeader()
        vh.setVisible(False)
        #vh.setSectionResizeMode(QHeaderView.ResizeToContents)

        #if adjustRowHeight:
        #    vh.setDefaultSectionSize(75)
        
        hh = table_view.horizontalHeader()
        #hh.setSectionResizeMode(QHeaderView.ResizeToContents)
        hh.setStretchLastSection(True)
        hh.setSectionsClickable(True)
        hh.setHighlightSections(True)
      
    def disconnect(self):        

        if self.session is not None:
            print("Closing Request Session")
            #logging.info("Closing Request Session")
            self.session.close()

        if self.login is not None:
            print("Closing Connection Information Dialog")
            #logging.info("Closing Connection Information Dialog")
            self.login.close()

        if self.shovelMenu is not None:
            print("Closing Shovel Messages window")
            self.shovelMenu.close()

        if self.exportMessagesDialog != {}:
            print("Closing Export Messages Dialog")
            #logging.info("Closing Export Messages Dialog")
            self.exportMessagesDialog.close()    

        if self.connection is not None:
            try:
                print("Closing AMQP Connection")
                #logging.info("Closing AMQP Connection")
                self.connection.close()   
            except:
                print("Closing AMQP Connection timed out or already closed.")
                #logging.error("Closing AMQP Connection timed out or already closed.")
       
        
        self.exportMessagesButton.setEnabled(False)      
        self.importMessagesButton.setEnabled(False)   
        self.disconnectButton.setEnabled(False) 
        self.shovelMessagesButton.setEnabled(False)     
        self.deleteMessagesButton.setEnabled(False)
        self.refreshButton.setEnabled(False)

        self.exportAction.setEnabled(False)      
        self.importAction.setEnabled(False)   
        self.disconnectAction.setEnabled(False)
        self.shovelAction.setEnabled(False) 
        self.refreshAction.setEnabled(False)  
        self.deleteAction.setEnabled(False)   
        self.exQBindingAction.setEnabled(False)
        self.extConfAction.setEnabled(False)
        self.impConfAction.setEnabled(False)
        self.extConfButton.setEnabled(False) 
        self.impConfButton.setEnabled(False) 
        self.patchConfAction.setEnabled(False)
        self.patchConfButton.setEnabled(False)
        self.exQBindingButton.setEnabled(False) 

        self.connectAction.setEnabled(True) 
        self.loginButton.setEnabled(True)  

        self.reset()
  
    def reset(self):
        self.exchange_list.clear()
        self.queue_list.clear()
       
        binData = []
        self.bindingtablemodelview.model().changeData(binData)

        msgData = []
        self.messagetablemodelview.model().changeData(msgData)

    
    def loginCancelled(self, cancelled):
        self._cancelled = cancelled
        #print(self._cancelled)

        if not self._cancelled:
            self.session = requests.Session() 
            self.sessionAvailable = True 

            #self.refreshButton.setEnabled(True)
            
            #self.setWindowTitle("RabbitMQ Utility - {}".format(self._webUrl))    # Set the window title

            self.populate()
            
            self.connection = RabbitMQPikaConnection.connect(RabbitMQPikaConnection, self, self._commandUrl, self._userId, self._password, self._certName, self._vhost, 'RabbitMQ_Util_Main')

            #print("self.connection = {}".format(self.connection))

            #self.exchange_list.setCurrentRow(0) # select first item
 
            #self.queue_list.setCurrentRow(0) # Select first item

            self.enableButtons()
    
    def populate(self):
        self.reset()

        self.exchange_list.clear()
        self.e_items = []
        self.q_items = []

        self.parser.read(os.environ['RMQ_COMMON_INI_FILE'])
        section_name = "DEFAULT"
        filteredVhosts = self.parser.get(section_name, 'filter.vhosts').split(",")
        filteredVhosts = [item.lower().strip() for item in filteredVhosts if item]

        #print(filteredVhosts, type(filteredVhosts))

        self.eitems = RestFunctions.exchange_list(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)
        for item in self.eitems:
            name = item["name"]           
            if any(filteredVhost in name for filteredVhost in filteredVhosts) or not filteredVhosts:
                if(len(name) != 0):
                    if len(name) == 0:
                        self.exchange_list.addItem("Default")
                        self.e_items.append("Default")
                    elif "federation" not in str(name):
                        self.exchange_list.addItem(str(name))        
                        self.e_items.append(str(name))

        self.queue_list.clear()
        self.qitems = RestFunctions.queue_list(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)
        for item in self.qitems:
            name = item["name"]        
            if any(filteredVhost in name for filteredVhost in filteredVhosts) or not filteredVhosts:
                if(len(name) != 0):
                    if len(name) == 0:
                        self.queue_list.addItem("Default")
                        self.q_items.append("Default")
                    elif "federation" not in str(name):
                        self.queue_list.addItem(str(name))        
                        self.q_items.append(str(name))

    def enableButtons(self):
        if self.sessionAvailable:
            
            #self.exportMessagesButton.setEnabled(True)      
            self.importMessagesButton.setEnabled(True)     
            self.disconnectButton.setEnabled(True)
            #self.shovelMessagesButton.setEnabled(True)   

            #self.exportAction.setEnabled(True)      
            self.importAction.setEnabled(True)     
            self.disconnectAction.setEnabled(True)
            #self.shovelAction.setEnabled(True)   
            self.exQBindingAction.setEnabled(True)
            self.extConfAction.setEnabled(True)
            self.impConfAction.setEnabled(True)
            self.extConfButton.setEnabled(True) 
            self.impConfButton.setEnabled(True) 
            self.exQBindingButton.setEnabled(True) 
            self.patchConfAction.setEnabled(True)
            self.patchConfButton.setEnabled(True)

            self.refreshAction.setEnabled(True)
            self.refreshButton.setEnabled(True)

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
    
    def getExportFileName(self, eFileName):
        self._exportFileName = eFileName
        #print(eFileName)

    def prettyPrintJson(self, val, sort=True, indents=4):
    
        if type(val) is str:
            return json.dumps(json.loads(val), sort_keys=sort, indent=indents)            
        else:
            return json.dumps(val, sort_keys=sort, indent=indents)
        return None

    def refresh(self):
        self.populate()

    def get_login(self):
        self.login.show()          
        self.loginmw.show()
        self.login.setReference(self.loginmw)

    def encryptString(self):
        self.encPass.show()
        self.epassmw.show()

    def decryptString(self):
        self.decPass.show()
        self.dpassmw.show()

    def exchangeQueueBindingAction(self):
        self.exqbindingMenu.show()
        self.eqbmw.show()
        #self.exqbindingMenu.show_login()
        self.exqbindingMenu.setConnection(self.connection, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._vhost, self._certName, self.eqbmw)

    def extractConfigAction(self):
        if self.sessionAvailable:
            self.extactConfig.show()            
            self.extconfmw.show()            

            self.extactConfig.setData(self.eitems, self.qitems, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName, self.extconfmw)
                        
    def exportMessages(self):
        if self.sessionAvailable and self.exportMessage != {}:
            #print("Exporting...")                                      
            val = self.prettyPrintJson(self.exportMessage)            

            self.exportMessagesDialog.show()            
            self.expmsgmw.show()                

            self.exportMessagesDialog.setMessage(val, self.expmsgmw) 
    
    def patchConfig(self):

        self.patchRConfig.setParams(self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)

        self.patchRConfig.populate()
        
        self.patchRConfig.initUi()
        
        self.patchRConfig.show()
        self.patconfmw.show()

        self.patchRConfig.setFrame(self.patconfmw)

    def shovelMessages(self):
         if self.sessionAvailable and self.exportMessage != {}:
                 
             messages = self.prettyPrintJson(self.exportMessage)
             
             os.linesep.join(messages.splitlines())

             self.shovelMenu.show()
             self.shovelmw.show()

             self.shovelMenu.setMessage(messages, self.shovelmw)
             self.shovelMenu.setConnection(self.connection, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)

    def deleteMessages(self):
        if self.sessionAvailable and (self.otherMessage != {} or self.exportMessage != {}):

            selectedMessages = self.prettyPrintJson(self.exportMessage)

            otherMessages = self.prettyPrintJson(self.otherMessage)
            
            os.linesep.join(selectedMessages.splitlines())

            os.linesep.join(otherMessages.splitlines())

            #print(selectedMessages, type(selectedMessages))

            #print(otherMessages, type(otherMessages))

            DeleteMessages.deleteMessages(self, self.queue_name, selectedMessages, self.sessionAvailable, self.connection, otherMessages)

            data = RestFunctions.queue_messages(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self.queue_name, self._userId, self._password, self._certName)               

            dummyData = []
            self.messagetablemodelview.model().changeData(dummyData)           

            self.messagetablemodelview.model().changeData(data)    
            
            self.messagetablemodelview.model().backupData()

            self.numMsgRecs.setText(str(self.messagetablemodelview.model().rowCount())) 

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Select a file to patch config", ".","JSON Files (*.json);; All Files(*.*)", options=options)
        if fileName:
            self.leFileName.setText(fileName)    


    def setFrame(self, frame):
        self.frame = frame

    def closewin(self):
   
        self.close()
        self.frame.close()

        self.shovelMenu.close()
        self.shovelmw.close()

        self.exqbindingMenu.close()
        self.eqbmw.close()

        self.exportMessagesDialog.close()
        self.expmsgmw.close()

        self.login.close()
        self.loginmw.close()

        self.encPass.close()
        self.epassmw.close()

        self.decPass.close()
        self.dpassmw.close()

        self.extactConfig.close()
        self.extconfmw.close()

        self.patchRConfig.close() 
        self.patconfmw.close() 

        if self.connection is not None and self.connection.is_open:
            self.connection.close()

        if self.session is not None:
            self.session.close()

        self._mainExited.emit(True)    

        #self.qapp.exit()

    
    def closeEvent(self, event):
       
        self._mainExited.emit(True)

        #self.close()
        #self.frame.close()

        self.shovelMenu.close()
        self.shovelmw.close()

        self.exqbindingMenu.close()
        self.eqbmw.close()

        self.exportMessagesDialog.close()
        self.expmsgmw.close()

        self.login.close()
        self.loginmw.close()

        self.encPass.close()
        self.epassmw.close()

        self.decPass.close()
        self.dpassmw.close()

        self.extactConfig.close()
        self.extconfmw.close()    

        self.patchRConfig.close() 
        self.patconfmw.close() 

        if self.connection is not None and self.connection.is_open:
            self.connection.close()

        if self.session is not None:
            self.session.close()
        
        #event.accept()
           

        #self.qapp.exit()

        