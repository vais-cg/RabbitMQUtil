from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QAction, QHBoxLayout, QPushButton,
QVBoxLayout, QMainWindow, QWidget, QVBoxLayout, QTableView, QAbstractItemView, 
QHeaderView, QLineEdit, QLabel, QFileDialog, QGroupBox, QStatusBar, QPlainTextEdit, QMessageBox, QComboBox, QStyleOptionComboBox, QItemDelegate, QStyle)

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QFont, QStandardItemModel, QStandardItem

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize, QAbstractTableModel, QModelIndex, QVariant, pyqtSlot, QPersistentModelIndex 

import json

import os

import sys

import decrypt

import requests

from configparser import ConfigParser

from messagebox import MessageBox

from restFunctions import RestFunctions

from rmqmodel import TableModel

from manage_ini import ConnectMenu

import styles
import windows

class resources(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self): 
        return self.name     

class MendConfig(QtWidgets.QMainWindow):

    def __init__(self, images_path, parser):
        super(MendConfig, self).__init__()          

        self.imagepath = images_path

        self.parser = parser

        self.parser.read(os.environ['RMQ_COMMON_INI_FILE'])
        section_name = "DEFAULT"
        self.filteredVhosts = self.parser.get(section_name, 'filter.vhosts').split(",")
        self.filteredVhosts = [item.lower().strip() for item in self.filteredVhosts if item]

        self.setWindowTitle("RabbitMQ Utility - Mend Configuration")    # Set the window title

        #self.setWindowIcon(QtGui.QIcon(self.imagepath + '/rabbit_icon.jpg'))

        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)  
        #------------------------------
        #self.app = app
        
        #------------------------------ 
        self.qapp = QApplication([])
        #V = self.qapp.desktop().screenGeometry()
        #h = V.height() - 600 
        #w = V.width() - 600

        h = 800 
        w = 1100

        self.resize(w, h)               

        self._webUrl = ""
        self._commandUrl = ""
        self._userId = ""
        self._password = ""
        self._vhost = ""
        self._certName = ""
        self._certPass = ""
        self._cancelled = True

        self.frame = None

        self.e_items = []
        self.q_items = []
        self.b_items_e = []
        self.b_items_q = []

        self.fileEx = []
        self.fileQ = []    
        self.fileBE2E = []
        self.fileBE2Q = []

        self.exArgsAdd = False
        self.qArgsAdd = False
        self.e2eArgsAdd = False
        self.e2qArgsAdd = False

        self.widget = QWidget()
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)       

        self.exrows = []
        self.qrows = []
        self.e2ebrows = []
        self.e2qrows = []

        self.exselectedrow = -1
        self.exselectedcolumn = -1

        self.qselectedrow = -1
        self.qselectedcolumn = -1

        self.exbselectedrow = -1
        self.exbselectedcolumn = -1

        self.qbselectedrow = -1
        self.qbselectedcolumn = -1
        
        self.sessionAvailable = False
        self.session = None    

        #self.login = LoginDialog(self.parser)
        self.login = ConnectMenu(self.parser, "./resources")
        
        self.login._cancelled.connect(self.loginCancelled)

        self.login._webUrl.connect(self.getWebConnectionUrl)
        self.login._commandUrl.connect(self.getCommandConnectionUrl)
        self.login._userId.connect(self.getConnectionUser)
        self.login._password.connect(self.getConnectionPassword)
        self.login._vhost.connect(self.getCconnectionVhost)
        self.login._certName.connect(self.getConnectionCertName)
        self.login._certPass.connect(self.getConnectionCertPass)
        self.loginmw = windows.ModernWindow(self.login, self.parser)

        # Create Connect
        self.connectAction = QAction(QIcon(self.imagepath + '/connect.png'), '&Connect', self)        
        self.connectAction.setShortcut('SHIFT+C')
        self.connectAction.setStatusTip('Connect')
        self.connectAction.triggered.connect(self.get_login)

        # Create refresh
        self.refreshAction = QAction(QIcon(self.imagepath + '/refresh.png'), '&Refresh', self)        
        self.refreshAction.setShortcut('CTRL+R')
        self.refreshAction.setStatusTip('Refresh')
        self.refreshAction.triggered.connect(self.refresh)      

        # Extract Config
        self.extConfAction = QAction(QIcon(self.imagepath + '/patch_config.png'),'&Patch Config', self)        
        self.extConfAction.setShortcut('Ctrl+M')
        self.extConfAction.setStatusTip('Patch Config')
        self.extConfAction.triggered.connect(self.patchconfig)

        #self.extConfAction.setEnabled(False)

        # Create Exit action
        self.exitAction = QAction(QIcon(self.imagepath + '/terminate.png'), '&Exit', self)        
        self.exitAction.setShortcut('ALT+F4')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.closewin)
       
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.connectAction)
        fileMenu.addAction(self.refreshAction)
        fileMenu.addAction(self.extConfAction)
        fileMenu.addAction(self.exitAction) 

        self.toolbar = self.addToolBar('')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)

        #self.toolbar.setIconSize(QSize(50,50))
        #self.toolbar.setGeometry(100, 100, 400, 400)
        
        #------------ Connect -------------
        self.loginButton = QAction(QIcon(self.imagepath + '/connect.png'), '&Connect', self)
        self.loginButton.setIconText('Connect')
        self.loginButton.setStatusTip("Click here to login")
        self.loginButton.triggered.connect(self.get_login)
        self.toolbar.addAction(self.loginButton)

        #------------ Refresh -------------
        self.refreshButton = QAction(QIcon(self.imagepath + '/refresh.png'), '&Refresh', self)
        self.refreshButton.triggered.connect(self.refresh)
        self.refreshButton.setStatusTip("Click here to reload json file")
        self.toolbar.addAction(self.refreshButton)         
        
        self.toolbar.addSeparator()

        #------------ Patch Config -------------
        self.genConfButton = QAction(QIcon(self.imagepath + '/patch_config.png'), '&Patch Config', self)
        self.genConfButton.setIconText('Patch Config')
        self.genConfButton.triggered.connect(self.patchconfig)
        #self.genConfButton.setEnabled(False)
        self.genConfButton.setStatusTip("Click here to mend exchange(s), queue(s) and binding(s) to json file") 
        self.toolbar.addAction(self.genConfButton)

        self.toolbar.addSeparator()      

        #------------ Exit -------------
        self.exitButton = QAction(QIcon(self.imagepath + '/terminate.png'), '&Exit', self)
        self.exitButton.triggered.connect(self.closewin)        
        self.exitButton.setStatusTip("Click here to exit") 
        self.toolbar.addAction(self.exitButton)           
    
    def createComponents(self):
        self.eGroupBox = QGroupBox("Exchanges")

        self.teheaders = ["Current Exchange", "New Exchange", "Exchange Type", "Durable?", "Auto Delete", "Internal", "Arguments"]       

        self.exchangeListTablemodel = QStandardItemModel()
        self.exchangeListTablemodelview = QTableView()
    
        #------------------------------------------------------------------------------------------------------------------

        self.qGroupBox = QGroupBox("Queues")
        
        self.tqheaders = ["Current Queue", "New Queue", "Durable?", "Auto Delete", "Arguments"]     

        self.queueListTablemodel = QStandardItemModel()
        self.queueListTablemodelview = QTableView()

        #------------------------------------------------------------------------------------------------------------------
        self.bE2EGroupBox = QGroupBox("Exchange To Exchange Bindings")

        self.tbe2eheaders = ["Source Exchange", "Target Exchange", "Routing Key", "Arguments"]     

        self.bindingE2EListTablemodel = QStandardItemModel()
        self.bindingE2EListTablemodelview = QTableView()

        #------------------------------------------------------------------------------------------------------------------
        self.bE2QGroupBox = QGroupBox("Exchange To Queue Bindings")
        
        self.tbe2qheaders = ["Exchange", "Queue", "Routing Key", "Arguments"]     

        self.bindingE2QListTablemodel = QStandardItemModel()
        self.bindingE2QListTablemodelview = QTableView()
        
        self.argsheaders = ["Key", "Value"]  

    def initUi(self):        

        self.createComponents()

        self.createTable(self.exchangeListTablemodelview, self.exchangeListTablemodel, self.teheaders, self.exrows, "exchange")

        self.createTable(self.queueListTablemodelview, self.queueListTablemodel, self.tqheaders, self.qrows, "queue")                    
       
        self.createTable(self.bindingE2EListTablemodelview, self.bindingE2EListTablemodel, self.tbe2eheaders, self.e2ebrows, "ebinding")

        self.createTable(self.bindingE2QListTablemodelview, self.bindingE2QListTablemodel, self.tbe2qheaders, self.e2qrows, "qbinding")
        
        #----------- Top UI ------------------
        self.vbox = QVBoxLayout()

        self.hbox2 = QHBoxLayout()
        self.leFileName = QLineEdit()
        self.leFileName.textChanged[str].connect(lambda: self.genConfButton.setEnabled(self.leFileName.text() != ""))
        self.leFileName.textChanged[str].connect(lambda: self.extConfAction.setEnabled(self.leFileName.text() != ""))

        self.hbox2.addWidget(QLabel("Export File Name:"))
        self.hbox2.addWidget(self.leFileName)

        self.fileChooser = QPushButton("Select File to Patch ...")        
        #self.fileChooser.clicked.connect(self.openFileNameDialog)
        self.hbox2.addWidget(self.fileChooser)     

        #--- Exchange UI -------------    
        
        self.hboxeqm = QHBoxLayout()

        vboxeqm = QVBoxLayout()
        vboxeqm.addWidget(self.exchangeListTablemodelview)        
        self.eGroupBox.setLayout(vboxeqm)

        '''
        dataine = []
        self.exargstablemodel = TableModel(dataine, self.argsheaders, self)
        self.exargstablemodelview = QTableView()  

        self.exArgsTable = QGroupBox("Exchange Arguments")
        self.exArgsAddButton = QPushButton("")
        self.exArgsDelButton = QPushButton("")
        vexargssub = self.createArgumentsUI(self.exargstablemodelview, self.exargstablemodel, "exchange", self.exArgsAddButton, self.exArgsDelButton)
        self.exArgsTable.setLayout(vexargssub)
        '''

        self.hboxeqm.addWidget(self.eGroupBox)
        #self.hboxeqm.addWidget(self.exArgsTable)
        self.hboxeqm.addStretch()
        self.eGroupBox.setMinimumWidth(1100)
        #self.exArgsTable.setMinimumWidth(300)
        #--- Queue UI -------------    

        self.hboxeqq = QHBoxLayout()

        vboxqsub = QVBoxLayout()
        vboxqsub.addWidget(self.queueListTablemodelview)
        self.qGroupBox.setLayout(vboxqsub)

        '''
        datainq = []
        self.qargstablemodel = TableModel(datainq, self.argsheaders, self)
        self.qargstablemodelview = QTableView() 
        self.qArgsTable = QGroupBox("Queue Arguments")
        self.qArgsAddButton = QPushButton("")
        self.qArgsDelButton = QPushButton("")
        vexargssubq = self.createArgumentsUI(self.qargstablemodelview, self.qargstablemodel, "queue", self.qArgsAddButton, self.qArgsDelButton)
        self.qArgsTable.setLayout(vexargssubq)
        '''

        self.hboxeqq.addWidget(self.qGroupBox)
        #self.hboxeqq.addWidget(self.qArgsTable)
        self.hboxeqq.addStretch()
        self.qGroupBox.setMinimumWidth(1100)
        #self.qArgsTable.setMinimumWidth(300)
        
        #--- Binding UI -------------    
        
        #--------E2E------
        self.hboxee2e = QHBoxLayout()

        vbindexlayout1 = QVBoxLayout()
        vbindexlayout1.addWidget(self.bindingE2EListTablemodelview)
        self.bE2EGroupBox.setLayout(vbindexlayout1)

        '''
        dataine2e = []
        self.e2eargstablemodel = TableModel(dataine2e, self.argsheaders, self)
        self.e2eargstablemodelview = QTableView() 
        self.e2eArgsTable = QGroupBox("Exchange To Exchange Arguments")
        self.e2eArgsAddButton = QPushButton("")
        self.e2eArgsDelButton = QPushButton("")
        ve2eargssubq = self.createArgumentsUI(self.e2eargstablemodelview, self.e2eargstablemodel, "ex2ex", self.e2eArgsAddButton, self.e2eArgsDelButton)
        self.e2eArgsTable.setLayout(ve2eargssubq)
        '''

        self.hboxee2e.addWidget(self.bE2EGroupBox)
        #self.hboxee2e.addWidget(self.e2eArgsTable)
        self.hboxee2e.addStretch()
        self.bE2EGroupBox.setMinimumWidth(1100)
        #self.e2eArgsTable.setMinimumWidth(300)
        
        #------ E2Q ---------------
        self.hboxee2q = QHBoxLayout()

        vbindqlayout2 = QVBoxLayout()
        vbindqlayout2.addWidget(self.bindingE2QListTablemodelview)
        self.bE2QGroupBox.setLayout(vbindqlayout2)

        '''
        dataine2q = []
        self.e2qargstablemodel = TableModel(dataine2q, self.argsheaders, self)
        self.e2qargstablemodelview = QTableView() 
        self.e2qArgsTable = QGroupBox("Exchange To Queue Arguments")
        self.e2qArgsAddButton = QPushButton("")
        self.e2qArgsDelButton = QPushButton("")
        ve2qargssubq = self.createArgumentsUI(self.e2qargstablemodelview, self.e2qargstablemodel, "ex2q", self.e2qArgsAddButton, self.e2qArgsDelButton)
        self.e2qArgsTable.setLayout(ve2qargssubq)
        '''

        self.hboxee2q.addWidget(self.bE2QGroupBox)
        #self.hboxee2q.addWidget(self.e2qArgsTable)
        self.hboxee2q.addStretch()
        self.bE2QGroupBox.setMinimumWidth(1100)
        #self.e2qArgsTable.setMinimumWidth(300)
        
        #-------------------------------------------------------
        
        self.vbox.addLayout(self.hbox2)        
        self.vbox.addLayout(self.hboxeqm)
        self.vbox.addLayout(self.hboxeqq)
        self.vbox.addLayout(self.hboxee2e)
        self.vbox.addLayout(self.hboxee2q)

        self.widget.setLayout(self.vbox)

        self.setCentralWidget(self.widget)   

    def createTable(self, tableview, tablemodel, headers, data, etype):
        
        tablemodel.setHorizontalHeaderLabels(headers)

        tableview.setModel(tablemodel)
        
        vhex = tableview.verticalHeader()
        vhex.setVisible(True)     
        
        hhex = tableview.horizontalHeader()      
        hhex.setDefaultAlignment(Qt.AlignHCenter)
     
        tableview.setColumnWidth(0, 200)
        tableview.setColumnWidth(1, 200)

        tableview.horizontalHeader().setStretchLastSection(True)

        tableview.setSelectionMode(QAbstractItemView.MultiSelection)
                      
        self.display(tableview, tablemodel, data, etype)   

    '''   
    def createArgumentsUI(self, tableview, tablemodel, component, addButton, delButton):
        vexargssub = QVBoxLayout() 
        
        hboxbuttonargs = QHBoxLayout()               

        addButton.setIcon(QIcon(self.imagepath + '/addrow.png'))
        addButton.setIconSize(QSize(25,25))
        addButton.setObjectName(component + 'addArgsKey')        
        
        delButton.setIcon(QIcon(self.imagepath + '/deleterow.png'))
        delButton.setIconSize(QSize(25,25))       
        delButton.setObjectName(component + 'delArgsKey')
        delButton.setEnabled(False)
        
        addButton.clicked.connect(lambda: self.buttonClicked(tableview, component))
        delButton.clicked.connect(lambda: self.buttonClicked(tableview, component))

        hboxbuttonargs.addWidget(QLabel("      "))
        hboxbuttonargs.addWidget(QLabel("      "))
        hboxbuttonargs.addWidget(QLabel("      "))
        hboxbuttonargs.addWidget(QLabel("      "))
        hboxbuttonargs.addWidget(addButton)
        hboxbuttonargs.addWidget(delButton)     
    
        tableview.setSelectionMode(QAbstractItemView.SingleSelection)   
                
        tableview.clicked.connect(self.showTableSelectedRowColumn)

        self.set_table_view_attributes(tableview, tablemodel)        
        vexargssub.addLayout(hboxbuttonargs)
        vexargssub.addWidget(tableview)        
        return vexargssub

    def set_table_view_attributes(self, table_view, table_model):     
        table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_view.setAlternatingRowColors(True)        
        table_view.setModel(table_model)        
        table_view.setSortingEnabled(True)                 

        # hide vertical header
        vh = table_view.verticalHeader()
        vh.setVisible(False)
     
        hh = table_view.horizontalHeader()        
        hh.setStretchLastSection(True)
        hh.setSectionsClickable(True)
        hh.setHighlightSections(True)
    
    def showTableSelectedRowColumn(self, index):
        if self.exArgsAdd:
            self.exArgsDelButton.setEnabled(True)

        if self.qArgsAdd:
            self.qArgsDelButton.setEnabled(True)
        
        if self.e2eArgsAdd:
            self.e2eArgsDelButton.setEnabled(True)
        
        if self.e2qArgsAdd:
            self.e2qArgsDelButton.setEnabled(True)

        self.tableSelectedRow = index.row()
        self.tableSelectedColumn = index.column()

    def buttonClicked(self, tableview, component):
        button = self.sender()
        #print(button.objectName())
        
        if not button: return  

        buttonObjectName = button.objectName()

        tableModel = tableview.model()        

        if buttonObjectName == component + "addArgsKey":
            data = [[]]
            self.addRow(tableModel, data)
            
            if component == "exchange":
                self.exArgsAdd = True
                self.qArgsAdd = False
                self.e2eArgsAdd = False
                self.e2qArgsAdd = False
            elif component == "queue":
                self.exArgsAdd = False
                self.qArgsAdd = True
                self.e2eArgsAdd = False
                self.e2qArgsAdd = False
            elif component == "ex2ex":
                self.exArgsAdd = False
                self.qArgsAdd = False
                self.e2eArgsAdd = True
                self.e2qArgsAdd = False
            elif component == "ex2q":
                self.exArgsAdd = False
                self.qArgsAdd = False
                self.e2eArgsAdd = False
                self.e2qArgsAdd = True
        elif buttonObjectName == component + "delArgsKey":
            if self.tableSelectedRow is not None:
                del tableModel.arraydata[self.tableSelectedRow]
                tableModel.changeData(tableModel.arraydata)
               
                if component == "exchange":
                    self.exArgsDelButton.setEnabled(False)
                elif component == "queue":
                    self.qArgsDelButton.setEnabled(False)
                elif component == "ex2ex":
                    self.e2eArgsDelButton.setEnabled(False)
                elif component == "ex2q":
                    self.e2qArgsDelButton.setEnabled(False)

                
    def populateHeaders(self, etype, argument_list):
        headerArray = []
        
        #print("argument_list: {}".format(argument_list))

        if argument_list != {}:
           
            args = argument_list.replace("{", "").replace("}", "").replace("'", "").split(",")
            for element in args:
                content = element.split(":")
                headerArray.append(content)
            
            if etype == "exchange" and self.exargstablemodelview is not None: 
                self.exargstablemodelview.model().changeData(headerArray)
            elif etype == "queue" and self.qargstablemodelview is not None: 
                self.qargstablemodelview.model().changeData(headerArray)
            elif etype == "ebinding" and self.e2eargstablemodelview is not None:
                self.e2eargstablemodelview.model().changeData(headerArray)
            elif etype == "qbinding" and self.e2qargstablemodelview is not None:
                self.e2qargstablemodelview.model().changeData(headerArray)
    '''

    def setrowcol(self, etype, row, column):
        if etype == "exchange": 
            self.exselectedrow = row
            self.exselectedcolumn = column
        elif etype == "queue": 
            self.qselectedrow = row
            self.qselectedcolumn = column
        elif etype == "ebinding":
            self.exbselectedrow = row
            self.exbselectedcolumn = column
        elif etype == "qbinding":
            self.qbselectedrow = row
            self.qbselectedcolumn = column

    def Combo_indexchanged(self, etype, data):
        combo = self.sender()
        row = combo.property('row')
        column = combo.property('column')
        index = combo.currentIndex()

        self.setrowcol(etype, row, column)
     
        #if self.exselectedrow != -1 or self.qselectedrow != -1 or self.exbselectedrow != -1 or self.qbselectedrow != -1:       
        #    self.populateHeaders(etype, data)
        
    def clickselected(self, index):
        self.selectedrow = index.row()
        self.selectedcolumn = index.column()

    def getdata(self, tableview, etype):
        self.setrowcol(etype, self.selectedrow, self.selectedcolumn)
        #print(row, column)
        if self.exselectedrow != -1 or self.qselectedrow != -1 or self.exbselectedrow != -1 or self.qbselectedrow != -1:  

            index = tableview.model().index(self.selectedrow, self.selectedcolumn, QModelIndex())

            if etype == "exchange": 
                argcolumn = 6
            elif etype == "queue": 
                argcolumn = 4
            elif etype == "ebinding":
                argcolumn = 3            
            elif etype == "qbinding":
                argcolumn = 3
            
            indexargs = tableview.model().index(self.selectedrow, argcolumn, QModelIndex())
            
            rowdata = str(tableview.model().data(index))
            arguments = str(tableview.model().data(indexargs))

            #self.populateHeaders(etype, arguments)            

    '''
    def addRow(self, table_model, data):
        rowcount = table_model.rowCount()
        if rowcount == 0:
            table_model.update(rowcount, data) 
        else:
            if len(table_model.arraydata[rowcount - 1][0]) != 0:
                table_model.update(rowcount, data) 
    '''

    def cleardata(self, tableview, tablemodel, data):
        for r in range(len(data)):
            tableview.selectRow(r)
            for model_index in tableview.selectionModel().selectedRows():
                index = QPersistentModelIndex(model_index)         
                tablemodel.removeRow(index.row())       

    def display(self, tableview, tablemodel, data, etype):
        
        row = tablemodel.rowCount()

        for d in data:
            for index in range(len(d)):                   
                tablemodel.setItem(row, index, QStandardItem(str(d[index])))              
                tablemodel.item(row, index).setEditable(True)      
                #tablemodel.layoutChanged.emit()

            lastcolumn = len(d) - 1
            # Hide Arguments column display in table view
            #tableview.setColumnHidden(lastcolumn, True)

            #print(lastcolumn, d[lastcolumn])

            tableview.setSelectionMode(QAbstractItemView.SingleSelection)    
            tableview.setSelectionBehavior(QAbstractItemView.SelectRows)  

            tableview.clicked.connect(self.clickselected)
            tableview.clicked.connect(lambda: self.getdata(tableview, etype))
            
            if etype == "exchange":                 
                self.addCombobox(tableview, tablemodel, etype, self.e_items, row, 1, d[lastcolumn])
                self.addCombobox(tableview, tablemodel, etype, ["direct", "topic", "fanout", "headers", "x-consistent-hash"], row, 2, d[lastcolumn], d[2])
                self.addCombobox(tableview, tablemodel, etype, ["True", "False"], row, 3, d[lastcolumn], d[3])
                self.addCombobox(tableview, tablemodel, etype, ["True", "False"], row, 4, d[lastcolumn], d[4])
                self.addCombobox(tableview, tablemodel, etype, ["True", "False"], row, 5, d[lastcolumn], d[5])
            elif etype == "queue":                
                self.addCombobox(tableview, tablemodel, etype, self.q_items, row, 1, d[lastcolumn])
                self.addCombobox(tableview, tablemodel, etype, ["True", "False"], row, 2, d[lastcolumn], d[2])
                self.addCombobox(tableview, tablemodel, etype, ["True", "False"], row, 3, d[lastcolumn], d[3])   
            elif etype == "ebinding":
                self.addCombobox(tableview, tablemodel, etype, self.b_items_e, row, 0, d[lastcolumn], d[0])    
                self.addCombobox(tableview, tablemodel, etype, self.b_items_e, row, 1, d[lastcolumn], d[1])

            elif etype == "qbinding":
                self.addCombobox(tableview, tablemodel, etype, self.b_items_e, row, 0, d[lastcolumn], d[0])    
                self.addCombobox(tableview, tablemodel, etype, self.b_items_q, row, 1, d[lastcolumn], d[1])    
            
            row = row + 1

    def addCombobox(self, tableview, tablemodel, etype, cbdata, row, column, arguments, searchtext=None):
        item = tableview.model().item(row, column)
        cbDelegate = QComboBox()
        cbDelegate.currentIndexChanged[str].connect(item.setText)
        #cbDelegate.currentIndexChanged[str].connect(lambda: self.Combo_indexchanged(etype, arguments))
        cbDelegate.activated[str].connect(lambda: self.Combo_indexchanged(etype, arguments))
        #print(cbdata)
        cbDelegate.addItems(cbdata)
        cbDelegate.setProperty('row', row)
        cbDelegate.setProperty('column', column)
        tableview.setIndexWidget(item.index(), cbDelegate)
        #tablemodel.item(row, column).setEditable(True)
        tableview.openPersistentEditor(tablemodel.index(row, column))

        tableview.setEditTriggers(QAbstractItemView.NoEditTriggers)   

        if searchtext:
            index = cbDelegate.findText(searchtext, Qt.MatchFixedString)
            if index >= 0:
                cbDelegate.setCurrentIndex(index)

    def getFileForImport(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Select a file to mend configuration", ".","JSON Files (*.json);; All Files(*.*)", options=options)
        data = None
        if fileName:            
            data = json.load(open(fileName))
        return data

    def populate(self):
        self.e_items = []
        self.q_items = []

        self.eitems = RestFunctions.exchange_list(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)

        for item in self.eitems:
            name = item["name"]           
            if any(filteredVhost in name for filteredVhost in self.filteredVhosts) or not self.filteredVhosts:
                if(len(name) != 0):
                    if len(name) == 0:
                        self.e_items.append("Default")
                    elif "federation" not in str(name):
                        self.e_items.append(str(name))
               
       
        self.qitems = RestFunctions.queue_list(RestFunctions, self, self.sessionAvailable, self.session, self._webUrl, self._userId, self._password, self._certName)
        for item in self.qitems:
            name = item["name"]        
            if any(filteredVhost in name for filteredVhost in self.filteredVhosts) or not self.filteredVhosts:
                if(len(name) != 0):
                    if len(name) == 0:
                        self.q_items.append("Default")
                    elif "federation" not in str(name):
                        self.q_items.append(str(name))
       
        fileData = self.getFileForImport() 
             
        if fileData is not None:     
            self.fileEx.clear()
            self.fileQ.clear()            
            self.fileBE2E.clear()
            self.fileBE2Q.clear()

            self.exrows = []
            self.qrows = []
            self.e2ebrows = []
            self.e2qrows = []

            for vhosts in fileData:                    
                for vh in fileData[vhosts]:
                    vhost = fileData[vhosts][vh]
                
                    exchanges = vhost["exchanges"]
                    queues = vhost["queues"]
                    bindings = vhost["bindings"]

                    for exchange in exchanges: 
                        exchdata = []
                        
                        self.fileEx.append(exchange)
                        
                        exch = exchanges[exchange]

                        etype = exch["type"]
                        durable = exch["durable"]
                        auto_delete = exch["auto_delete"]
                        internal = exch["internal"]
                        arguments = exch["arguments"]
                               
                        exchdata = [exchange, [], etype, str(durable), str(auto_delete), str(internal), str(arguments)]

                        self.exrows.append(exchdata)

                   
                    for queue in queues:    
                        qdata = []   
                        self.fileQ.append(queue)

                        qu = queues[queue]
                            
                        durable = qu["durable"]
                        auto_delete = qu["auto_delete"]
                        arguments = qu["arguments"]

                        qdata = [queue, [], str(durable), str(auto_delete), str(arguments)]

                        self.qrows.append(qdata)

                    for binding in bindings:                      

                        bind = bindings[binding]

                        source = binding.split("_")[0]
                        destination = binding         
                        routing_key = bind["routing_key"]                                
                        arguments = bind["arguments"]         
                        
                        destination_type = bind["destination_type"]

                        if destination_type == "exchange":
                            e2ebdata = []
                            self.fileBE2E.append(source)
                            self.b_items_e = self.e_items.copy()

                            e2ebdata = [str(source), str(destination), str(routing_key), str(arguments)]

                            self.e2ebrows.append(e2ebdata)       

                        elif destination_type == "queue": 
                            self.fileBE2Q.append(source)
                            self.b_items_q = self.q_items.copy()

                            e2qbdata = [str(source), str(destination), str(routing_key), str(arguments)]

                            self.e2qrows.append(e2qbdata)

                        #print("source:{source}\tdestination:{target}".format(source=source, target=destination))                    
                        

    def loginCancelled(self, cancelled):
        self._cancelled = cancelled
        #print(self._cancelled)

        if not self._cancelled:
            self.session = requests.Session() 
            self.sessionAvailable = True 
            #self.populate() 
            self.refresh()                     

    def get_login(self):
        self.login.show()          
        self.loginmw.show()
        self.login.setReference(self.loginmw)

    def setParams(self, sessionAvailable, session, _webUrl, _userId, _password, _certName):
        self.sessionAvailable = sessionAvailable
        self.session = session
        self._webUrl = _webUrl
        self._userId =  _userId
        self._password = _password
        self._certName = _certName

    def setFrame(self, frame):
        self.frame = frame

    def refresh(self):      
        binData1 = []
        self.exargstablemodelview.model().changeData(binData1)

        binData2 = []
        self.qargstablemodelview.model().changeData(binData2)

        binData3 = []
        self.e2eargstablemodelview.model().changeData(binData3)

        binData4 = []
        self.e2qargstablemodelview.model().changeData(binData4)

        self.populate()
       
        self.cleardata(self.exchangeListTablemodelview, self.exchangeListTablemodel, self.exrows)       
        self.display(self.exchangeListTablemodelview, self.exchangeListTablemodel, self.exrows, "exchange")

        self.cleardata(self.queueListTablemodelview, self.queueListTablemodel, self.qrows)       
        self.display(self.queueListTablemodelview, self.queueListTablemodel, self.qrows, "queue")       

        self.cleardata(self.bindingE2EListTablemodelview, self.bindingE2EListTablemodel, self.e2ebrows)                    
        self.display(self.bindingE2EListTablemodelview, self.bindingE2EListTablemodel, self.e2ebrows, "ebinding")

        self.cleardata(self.bindingE2QListTablemodelview, self.bindingE2QListTablemodel, self.e2qrows)       
        self.display(self.bindingE2QListTablemodelview, self.bindingE2QListTablemodel, self.e2qrows, "qbinding")

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
    
    def getdatafromtable(self, tableview, tablemodel):
        
        row = []
        for r in range(tablemodel.rowCount()):
            rowdata = []
            for c in range(tablemodel.columnCount()):
                index = tableview.model().index(r, c, QModelIndex())
                rowdata.append(str(tableview.model().data(index)))

            row.append(rowdata)
        return row

    def patchconfig(self):       
       
        erows = self.getdatafromtable(self.exchangeListTablemodelview, self.exchangeListTablemodel)       
        qrows = self.getdatafromtable(self.queueListTablemodelview, self.queueListTablemodel)
        e2erows = self.getdatafromtable(self.bindingE2EListTablemodelview, self.bindingE2EListTablemodel)
        e2qrows = self.getdatafromtable(self.bindingE2QListTablemodelview, self.bindingE2QListTablemodel)     
        
        #-------------- exchange ------------------
        ex_array = {}
        
        e = 0
        for row in erows:
            exname = row[1]
            extype = row[2]
            durable = row[3]
            auto_delete = row[4]
            internal = row[5]
            arguments = row[6]

            data = {}
            data["type"] = extype
            data["durable"] = "true" if durable else "false"
            data["auto_delete"] = "true" if auto_delete else "false"
            data["internal"] = "true" if internal else "false"
            data["arguments"] = {} if arguments is None else arguments

            ex_array[exname + "_" + str(e)] = data
            e = e + 1

        #---------- queue -----------------------------------

        q_array = {}
        
        q = 0
        for row in qrows:
            qname = row[1]
            durable = row[2]
            auto_delete = row[3]
            arguments = row[4]

            data = {}
            data["durable"] = "true" if durable else "false"
            data["auto_delete"] = "true" if auto_delete else "false"
            data["arguments"] = {} if arguments is None else arguments
            
            qdata[resources(qname)]= data

            q_array[qname + "_" + str(q)] = data
            q = q + 1

        #------------- binding - exchange2exchange / exchange2queue ----------------

        binding_array = {}
        
        i = 0
        for qb in e2erows:
            source = qb[0]
            destination = qb[1]
            destination_type = "exchange"
            routing_key = qb[2]
            arguments = qb[3]
            
            qbData = {}
            qbData["destination"] = destination 
            #qbData["destination"] = source 
            #qbData["source"] = source
            qbData["destination_type"] = destination_type 
            qbData["routing_key"] = routing_key
            qbData["arguments"] = arguments

            binding_array[source + "_" + str(i)] = qbData
            i = i + 1
        #######

        for qb in e2qrows:        
            source = qb[0]
            destination = qb[1]
            destination_type = "queue"
            routing_key = qb[2]
            arguments = qb[3]

            qbData = {}
            qbData["destination"] = destination 
            #qbData["destination"] = source
            #qbData["source"] = source
            qbData["destination_type"] = destination_type 
            qbData["routing_key"] = routing_key
            qbData["arguments"] = arguments            

            binding_array[source + "_" + str(i)] = qbData
            i = i + 1

        eqs = {}
        
        eqs.update( { "exchanges": ex_array } )
        eqs.update( { "queues": q_array } )
        eqs.update( { "bindings": binding_array } )

        vhost = { "/":  eqs} 
        #print(vhost)

        output = {}
        #output["version"] = "0.1"
        #output["broker"] = "rmq-1"
        #output["user"] = "test123"
        output["vhosts"] = vhost 

        print(output)

        #fileName = "C:\\Users\\vais\Documents\\Scripts\\python\\RabbitMQ\\mend.json"
        fileName = self.leFileName.toPlainText()
        if len(fileName) > 0:
            with open(fileName, 'w') as json_file:
                #json_file.write(self.leMessages.toPlainText())
                json_file.write(json.dumps(output, indent=2))
                MessageBox.message(QMessageBox.Information, "RabbitMQ Mend Config", "Exchange(s), Queue(s) and Binding(s) Exported!", 
                                               "Please see file: {file} for details.".format(file=fileName)) 

        s = open(fileName).read()
        s = s.replace("[", "")
        s = s.replace("]", "")
        s = s.replace("\"{", "{")
        s = s.replace("}\"", "}")
        s = s.replace("'", "\"")

        f = open(fileName, 'w')
        f.write(s)
        f.close()

    def getExportFileName(self, eFileName):
        self._exportFileName = eFileName
        #print(eFileName)

    def closewin(self):
        if self is not None:
            self.close()

        if self.frame is not None: 
            self.frame.close()

        self.login.close()
        self.loginmw.close()

        #self.qapp.exit()      
    
    def closeEvent(self, event):    
        if self is not None:
            self.close()

        if self.frame is not None: 
            self.frame.close()

        self.login.close()
        self.loginmw.close()

       

        #self.qapp.exit()      