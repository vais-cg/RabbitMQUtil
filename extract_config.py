import json

import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QAction, QHBoxLayout, QPushButton,
QVBoxLayout, QMainWindow, QWidget, QVBoxLayout, QTableView, QAbstractItemView, 
QHeaderView, QLineEdit, QLabel, QFileDialog, QGroupBox, QStatusBar, QPlainTextEdit, QMessageBox)

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QFont

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize

from rmqmodel import TableModel

from restFunctions import RestFunctions

from messagebox import MessageBox

from configparser import ConfigParser

from collections import defaultdict

__IMAGES_PATH__ = ""

class resources(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self): 
        return self.name     

class ExtractConfigMenu(QtWidgets.QMainWindow):

    def __init__(self, images_path, parser):
        #super().__init__()
        super(ExtractConfigMenu, self).__init__()

        __IMAGES_PATH__ = images_path

        self.parser = parser

        self.parser.read(os.environ['RMQ_COMMON_INI_FILE'])
        section_name = "DEFAULT"
        self.filteredVhosts = self.parser.get(section_name, 'filter.vhosts').split(",")
        self.filteredVhosts = [item.lower().strip() for item in self.filteredVhosts if item]

        self.setWindowTitle("RabbitMQ Utility - Export Resources")    # Set the window title

        #self.setWindowIcon(QtGui.QIcon(__IMAGES_PATH__ + '/rabbit_icon.jpg'))

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
        self._userId = ""
        self._password = ""
        self._certName = ""
        self.sessionAvailable = False
        self.session = None        

        self.frame = None

        self.widget = QWidget()
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)               

        # Extract Config
        self.extConfAction = QAction(QIcon(__IMAGES_PATH__ + '/export_config.png'),'&Generate Config', self)        
        self.extConfAction.setShortcut('Ctrl+G')
        self.extConfAction.setStatusTip('Generate Config')
        self.extConfAction.triggered.connect(self.generate)
        self.extConfAction.setEnabled(False)

        # Create Exit action
        self.exitAction = QAction(QIcon(__IMAGES_PATH__ + '/terminate.png'), '&Exit', self)        
        self.exitAction.setShortcut('ALT+F4')
        self.exitAction.setStatusTip('Exit application')
        self.exitAction.triggered.connect(self.closewin)
       
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(self.extConfAction)
        fileMenu.addAction(self.exitAction) 

        self.toolbar = self.addToolBar('')
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)

        #self.toolbar.setIconSize(QSize(50,50))
        #self.toolbar.setGeometry(100, 100, 400, 400)

        #------------ Extract -------------
        self.genConfButton = QAction(QIcon(__IMAGES_PATH__ + '/export_config.png'), '&Generate Config', self)
        self.genConfButton.setIconText('Generate Config')
        self.genConfButton.triggered.connect(self.generate)
        self.genConfButton.setEnabled(False)
        self.genConfButton.setStatusTip("Click here to extract exchange(s), queue(s) and binding(s) to json file") 
        self.toolbar.addAction(self.genConfButton)

        self.toolbar.addSeparator()

        self.exitButton = QAction(QIcon(__IMAGES_PATH__ + '/terminate.png'), '&Exit', self)
        self.exitButton.triggered.connect(self.closewin)        
        self.exitButton.setStatusTip("Click here to exit") 
        self.toolbar.addAction(self.exitButton)         


        self.eGroupBox = QGroupBox("Exchanges")
               
        eheaders = ["Name", "Type", "Durable?", "Auto Delete?", "Internal?", "Arguments"]       
        self.datae = []
        self.exchangeListTableSelectedRow = 0
        
        self.exchangeListTablemodel = TableModel(self.datae, eheaders, self)
        self.exchangeListTablemodel.setName("EXCHANGE_LIST")
        self.exchangeListTablemodelview = QTableView()  
        self.exchangeListTablemodelview.setSelectionMode(QAbstractItemView.MultiSelection) 
        
        self.set_table_view_attributes(self.exchangeListTablemodelview, self.exchangeListTablemodel, False, self.datae)      

      
        #self.exchangeListTablemodelview.clicked.connect(lambda: self.exchangeListTableClick(self.exchangeListTablemodel))       
        #self.exchangeListTablemodelview.selectionModel().selectionChanged.connect(lambda: self.bindingTableClick(self.exchangeListTablemodel))       

        #---------------------------------------------------------------
        self.qGroupBox = QGroupBox("Queue")

        qheaders = ["Name", "Durable?", "Auto Delete?", "Arguments"]       
        self.dataq = []
        self.queueListTableSelectedRow = 0
        
        self.queueListTablemodel = TableModel(self.dataq, qheaders, self)
        self.queueListTablemodel.setName("QUEUE_LIST")
        self.queueListTablemodelview = QTableView()  
        self.queueListTablemodelview.setSelectionMode(QAbstractItemView.MultiSelection)   
        
        self.set_table_view_attributes(self.queueListTablemodelview, self.queueListTablemodel, False, self.dataq)        
        
        #self.queueListTablemodelview.clicked.connect(lambda: self.queueTableClick(self.queueListTablemodel))       
        #self.queueListTablemodelview.selectionModel().selectionChanged.connect(lambda: self.bindingTableClick(self.queueListTablemodel))       


        self.extConfGroupBox = QGroupBox("Extracted Configuration")      


        #----------- Top UI ------------------
        hbox = QHBoxLayout()

        eqvLayout = QVBoxLayout()

        vboxexsub = QVBoxLayout()
        hExSearchLayout = QHBoxLayout()
        hExSearchLayout.addWidget(QLabel("Search Exchange(s):"))
        self.searchExchange=QLineEdit()
        hExSearchLayout.addWidget(self.searchExchange)
        self.searchExchange.textEdited.connect(lambda: self.searchLineEditied (self.exchangeListTablemodel, self.searchExchange))
        self.searchExchange.returnPressed.connect(lambda: self.searchLineEditied (self.exchangeListTablemodel, self.searchExchange))
        vboxexsub.addLayout(hExSearchLayout)
        vboxexsub.addWidget(self.exchangeListTablemodelview)
        self.eGroupBox.setLayout(vboxexsub)

        vboxqsub = QVBoxLayout()
        hQSearchLayout = QHBoxLayout()
        hQSearchLayout.addWidget(QLabel("Search Queue(s):"))
        self.searchQueue=QLineEdit()
        hQSearchLayout.addWidget(self.searchQueue)
        self.searchQueue.textEdited.connect(lambda: self.searchLineEditied (self.queueListTablemodel, self.searchQueue))
        self.searchQueue.returnPressed.connect(lambda: self.searchLineEditied (self.queueListTablemodel, self.searchQueue))
        vboxqsub.addLayout(hQSearchLayout)
        vboxqsub.addWidget(self.queueListTablemodelview)
        self.qGroupBox.setLayout(vboxqsub)

        hbox.addWidget(self.eGroupBox)
        hbox.addWidget(self.qGroupBox)

        #------------- Bottom UI ---------------
        hbox1 = QHBoxLayout()
        #self.searchExchangeOrQueue=QLineEdit()
        
        vboxEQ = QVBoxLayout()
        
        self.leMessages = QPlainTextEdit(self)
        self.leMessages.resize(500, 500)        
        self.leMessages.setStyleSheet(
        """QPlainTextEdit {background-color: #333;
                           color: #00FF00;
                           font-family: Courier;}""")

        vboxEQ.addWidget(self.leMessages)

        hbox2 = QHBoxLayout()
        self.leFileName = QLineEdit()
        self.leFileName.textChanged[str].connect(lambda: self.genConfButton.setEnabled(self.leFileName.text() != ""))
        self.leFileName.textChanged[str].connect(lambda: self.extConfAction.setEnabled(self.leFileName.text() != ""))

        hbox2.addWidget(QLabel("Export File Name:"))
        hbox2.addWidget(self.leFileName)

        self.fileChooser = QPushButton("Select File ...")        
        self.fileChooser.clicked.connect(self.openFileNameDialog)
        hbox2.addWidget(self.fileChooser)   

        
        self.extConfGroupBox.setLayout(vboxEQ)

        hbox1.addWidget(self.extConfGroupBox)
       
        vbox = QVBoxLayout()
                
        vbox.addLayout(hbox2)

        vbox.addLayout(hbox)

        vbox.addLayout(hbox1)

        self.widget.setLayout(vbox)

        self.setCentralWidget(self.widget)          
   
    def set_table_view_attributes(self, table_view, table_model, adjustRowHeight, data):     

        table_view.setStyleSheet("""
            QTableView {
                selection-background-color: palette(Highlight);
                selection-color: palette(HighlightedText)
            },
            QHeaderView::section{Background-color:rgb(67, 255, 127);border-radius:20px;}
        """)

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

    def searchLineEditied(self, tableModel, searchText):
        rows = tableModel.rowCount()
        tableModel.backupData()
        if rows:        
            tableModel.setFilter(searchText.text())

    def reset(self):
        self.leFileName.setText("")

        eData = []
        self.exchangeListTablemodelview.model().changeData(eData)

        qData = []
        self.queueListTablemodelview.model().changeData(qData)

    def populateExchangeList(self, exchange_list, userId):
        row = 0
        emodelview = self.exchangeListTablemodelview
        for item in exchange_list:
            arrItems = []
            name = item["name"]
            if any(filteredVhost in name for filteredVhost in self.filteredVhosts) or not self.filteredVhosts:
                if(len(name) != 0) and "federation" not in str(name):
                    #self.exchange_list.addItem("Default" if len(name) == 0 else str(name))
                    name = "Default" if len(name) == 0 else str(name)
                    etype = item["type"]
                    durable = item["durable"]
                    auto_delete = item["auto_delete"]
                    internal = item["internal"]
                    arguments = dict(item["arguments"])
                    
                    #print(name, etype, durable, auto_delete, internal, arguments)
                    
                    arrItems.append(name)
                    arrItems.append(etype)
                    arrItems.append(durable)
                    arrItems.append(auto_delete)
                    arrItems.append(internal)
                    arrItems.append(arguments)

                    self.datae.append(arrItems)
                    row = row + 1

        emodelview.model().changeData(self.datae)
        if emodelview.model().rowCount() > 0:
            #emodelview.setCurrentIndex(emodelview.model().index(0,0))
            self.exchangeListTablemodelview.model().backupData()

    def populateQueueList(self, queue_list, userId):
        row = 0
        qmodelview = self.queueListTablemodelview
        for item in queue_list:
            arrItems = []
            name = item["name"]        
            if any(filteredVhost in name for filteredVhost in self.filteredVhosts) or not self.filteredVhosts:
                if(len(name) != 0) and "federation" not in str(name):
                    #self.queue_list.addItem("Default" if len(name) == 0 else str(name))
                    name = "Default" if len(name) == 0 else str(name)
                    durable = False if not item["durable"] else True
                    auto_delete = False if not item["auto_delete"] else True
                    arguments = dict(item["arguments"])
                    
                    #print(name, durable, auto_delete, arguments)
                    arrItems.append(name)                    
                    arrItems.append(durable)
                    arrItems.append(auto_delete)
                    arrItems.append(arguments)

                    self.dataq.append(arrItems)
                    row = row + 1

        qmodelview.model().changeData(self.dataq) 
        if qmodelview.model().rowCount() > 0:
            #qmodelview.setCurrentIndex(qmodelview.model().index(0,0))   
            self.queueListTablemodelview.model().backupData()          

    def setData(self, exchange_list, queue_list, sessionAvailable, session, _webUrl, userId, _password, _certName, _frame):        

        self._webUrl = _webUrl
        self._userId = userId
        self._password = _password
        self._certName = _certName
        self.sessionAvailable = sessionAvailable
        self.session = session
        self.frame = _frame

        self.reset()       

        self.populateExchangeList(exchange_list, userId)
        self.populateQueueList(queue_list, userId)     

    def generate(self):
        self.selectedExchanges = {}
        self.selectedQueues = {}

        exchanges = self.exchangeListTablemodelview.selectedIndexes()
        queues = self.queueListTablemodelview.selectedIndexes()

        erows = sorted(set(index.row() for index in self.exchangeListTablemodelview.selectedIndexes()))
        qrows = sorted(set(index.row() for index in self.queueListTablemodelview.selectedIndexes()))

        ex_array = {}
        q_array = {}
        eqb_array = {}

        exmodel = self.exchangeListTablemodelview.model()
        qmodel = self.queueListTablemodelview.model()
               
        for row in erows:
            #print('ERow %d is selected' % row)  

            exname = exmodel.arraydata[row][0]
            extype = exmodel.arraydata[row][1]
            durable = exmodel.arraydata[row][2]
            auto_delete = exmodel.arraydata[row][3]
            internal = exmodel.arraydata[row][4]
            arguments = exmodel.arraydata[row][5]

            data = {}
            data["type"] = extype
            data["durable"] = durable
            data["auto_delete"] = auto_delete
            data["internal"] = internal
            data["arguments"] = arguments
            
            exdata = {}
            exdata[exname] = data

            exbindings = RestFunctions.exchange_bindings(RestFunctions, self, self.session, self._webUrl, exname, self._userId, self._password, self._certName)

            #print(exbindings)

              
            i = 0
            for eb in exbindings:
                source = eb[1]
                destination = eb[4]
                destination_type = eb[5]
                routing_key = eb[6]
                arguments = eb[9]

                #print(destination, source, destination_type, routing_key, arguments)
                exbData = {}
                exbData["destination"] = destination 
                #exbData["source"] = source
                exbData["destination_type"] = destination_type 
                exbData["routing_key"] = routing_key
                exbData["arguments"] = arguments

                #print(exbData)

                eqb_array[source + "_" + str(i)] = exbData
                i = i + 1


            ex_array.update(exdata)         

        for row in qrows:
            #print('QRow %d is selected' % row)

            qname = qmodel.arraydata[row][0]
            durable = qmodel.arraydata[row][1]
            auto_delete = qmodel.arraydata[row][2]
            arguments = qmodel.arraydata[row][3]

            data = {}
            data["durable"] = durable
            data["auto_delete"] = auto_delete
            data["arguments"] = arguments

            qdata = {}
            qdata[qname]= data             
                        
            q_array.update(qdata)           
        
        eqs = {}
        eqs["exchanges"] = ex_array
        eqs["queues"] = q_array
        eqs["bindings"] = eqb_array
        
        vhost = { "/":  eqs} 
        #print(vhost)

        output = {}
        #output["version"] = "0.1"
        #output["broker"] = "rmq-1"
        #output["user"] = "test123"
        output["vhosts"] = vhost 

        print(output)

        #print(json.dumps(output))
        jstr = json.dumps(output, indent=2)

        self.leMessages.setPlainText(jstr)

        fileName = self.leFileName.text()
        if len(fileName) > 0:
            with open(fileName, 'w') as json_file:
                json_file.write(self.leMessages.toPlainText())
                MessageBox.message(QMessageBox.Information, "RabbitMQ Export", "Exchange(s), Queue(s) and Binding(s) Exported!", 
                                               "Please see file: {file} for details.".format(file=fileName)) 

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Select a file to export message(s)", ".","JSON Files (*.json);; All Files(*.*)", options=options)
        if fileName:
            self.leFileName.setText(fileName)    

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