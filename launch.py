import sys

import os

import logging

import styles
import windows

from configparser import ConfigParser

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QVBoxLayout, QMainWindow, QRadioButton,  
QWidget,  QLabel, QGroupBox, QStatusBar, QPushButton)

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer

from rabbitmq_details import RMQUMenu

import weakref

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(name)s - %(levelname)s - %(message)s')   

class StartRabbitMQUtil(QtWidgets.QMainWindow):
    
    def __init__(self, parser):
        super(StartRabbitMQUtil, self).__init__()        

        self.setWindowTitle("RabbitMQ Utility Launcher")    # Set the window title
        #------------------------------
        #self.app = app
        self.parser = parser

        self.frame = None

        self.env = ""

        #------------------------------ 
        self.qapp = QApplication([])
        #V = self.qapp.desktop().screenGeometry()
        #h = V.height() - 600 
        #w = V.width() - 600

        h = 200 
        w = 250

        self.resize(w, h)

        self.widget = QWidget()           

        self.rmqmw = None
        self.rmqMenu = None     

        self.mainexit = False 

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.envBox = QGroupBox("Environment")
        
        hbox = QHBoxLayout()

        vbrb = QVBoxLayout()
        

        #hbox1 = QHBoxLayout()
        self.envDev = QRadioButton("Development")
        self.envQa = QRadioButton("Qa")
        self.envProd = QRadioButton("Production")
        
        self.envDev.toggled.connect(lambda:self.btnstate(self.envDev))
        self.envQa.toggled.connect(lambda:self.btnstate(self.envQa))
        self.envProd.toggled.connect(lambda:self.btnstate(self.envProd))
        
        vbrb.addWidget(self.envDev)
        vbrb.addWidget(self.envQa)
        vbrb.addWidget(self.envProd)

        #hbox1.addLayout(vbrb)

        self.envBox.setLayout(vbrb)
        hbox.addWidget(self.envBox)

        hbox2 = QHBoxLayout()
        self.launchButton = QPushButton("Launch")
        self.launchButton.setEnabled(False)
        self.launchButton.clicked.connect(self.launch)

        self.closeButton = QPushButton("Reset")
        self.closeButton.setEnabled(False)
        self.closeButton.clicked.connect(self.closermq)

        exitButton =  QPushButton("Exit")
        exitButton.clicked.connect(self.closewin)

        hbox2.addWidget(self.launchButton)   
        hbox2.addWidget(self.closeButton)   
        hbox2.addWidget(exitButton)   

        vbox = QVBoxLayout()
        
        vbox.addLayout(hbox)
        vbox.addLayout(hbox2)
        
        self.widget.setLayout(vbox)

        self.setCentralWidget(self.widget)     

    def btnstate(self,b):
        radioButton = b.text()

        if len(radioButton) != 0 and b.isChecked() == True:
            self.launchButton.setEnabled(True)

        if radioButton == "Development" and b.isChecked() == True:
            self.env = "dev"
        elif radioButton == "Qa" and b.isChecked() == True:
            self.env = "qa"    
        else:
            self.env = "prod"

    def closermq(self):
        
        self.envDev.setEnabled(True)
        self.envQa.setEnabled(True)
        self.envProd.setEnabled(True)

        self.envDev.setAutoExclusive(False)
        self.envDev.setChecked(False)
        self.envDev.setAutoExclusive(True)

        self.envQa.setAutoExclusive(False)
        self.envQa.setChecked(False)
        self.envQa.setAutoExclusive(True)

        self.envProd.setAutoExclusive(False)
        self.envProd.setChecked(False)
        self.envProd.setAutoExclusive(True)

        if  self.rmqmw is not None:
            self.rmqmw.close() 
        
        if self.rmqMenu is not None:
            self.rmqMenu.close()

        self.closeButton.setEnabled(False)

    def launch(self):
        
        self.closeButton.setEnabled(True)

        iniFile = "./resources/properties/{env}/{env}_rabbitmq.ini".format(env=self.env)
        
        os.environ['RMQ_INI_FILE'] = iniFile

        self.parser.read(iniFile)        
        
        self.rmqMenu = RMQUMenu(self.parser)   
        self.rmqmw = windows.ModernWindow(window=self.rmqMenu, parser=self.parser)
        self.rmqMenu.setFrame(self.rmqmw)

        self.rmqMenu._mainExited.connect(self.mainexited)
      
        self.rmqmw.show()
        self.rmqMenu.show()

        self.envDev.setEnabled(False)
        self.envQa.setEnabled(False)
        self.envProd.setEnabled(False)

        self.launchButton.setEnabled(False)
        
    def mainexited(self, exited):
        self.mainexit = exited

    def setFrame(self, frame):
        self.frame = frame

    def closewin(self):

        if not self.mainexit:
            if  self.rmqmw is not None:
                self.rmqmw.close() 
            
            if self.rmqMenu is not None:
                self.rmqMenu.close()
           

        #self.close()
        #self.frame.close()

        self.qapp.quit()
    
    
    def closeEvent(self, event):
        if not self.mainexit:
            if  self.rmqmw is not None:
                self.rmqmw.close() 
            
            if self.rmqMenu is not None:
                self.rmqMenu.close()
           

        #self.close()
        #self.frame.close()

        self.qapp.quit()
    
def main():   
   
    app = QtWidgets.QApplication(sys.argv)
    parser = ConfigParser()

    menu = StartRabbitMQUtil(parser)        
    #menu.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowCloseButtonHint)

    os.environ['RMQ_COMMON_INI_FILE'] = './resources/properties/common.ini'

    styles.light(app)
    #styles.dark(app)
    mw = windows.ModernWindow(window=menu, parser=parser, movetocenter=False)
    mw.show() 

    menu.setFrame(mw)
    menu.show()   

    app.exec()        

   
if __name__ == '__main__':
    main()        