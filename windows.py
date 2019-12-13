import os
from os.path import join, dirname, abspath

from qtpy.QtCore import Qt, QMetaObject, Signal, Slot, QSize
from qtpy.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QToolButton,
                            QLabel, QSizePolicy, QApplication, QDesktopWidget, QLabel)
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QPixmap, QPixmapCache

from configparser import ConfigParser

import qtpy

QT_VERSION = tuple(int(v) for v in qtpy.QT_VERSION.split('.'))
""" tuple: Qt version. """

_FL_STYLESHEET = join(dirname(abspath(__file__)), 'resources/css/frameless.qss')
""" str: Frameless window stylesheet. """

#__INI_FILE__ = join(dirname(abspath(__file__)), 'resources/properties/rabbitmq.ini')
#__INI_FILE__ = os.environ['RMQ_INI_FILE']

#parser = ConfigParser()
#parser.read(__INI_FILE__)

class WindowDragger(QWidget):
    """ Window dragger.

        Args:
            window (QWidget): Associated window.
            parent (QWidget, optional): Parent widget.
    """

    doubleClicked = Signal()

    def __init__(self, window, parent=None):
        QWidget.__init__(self, parent)

        self._window = window
        self._mousePressed = False

    def mousePressEvent(self, event):
        self._mousePressed = True
        self._mousePos = event.globalPos()
        self._windowPos = self._window.pos()

    def mouseMoveEvent(self, event):
        if self._mousePressed:
            self._window.move(self._windowPos +
                              (event.globalPos() - self._mousePos))

    def mouseReleaseEvent(self, event):
        self._mousePressed = False

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()


class ModernWindow(QWidget):
    """ Modern window.

        Args:
            w (QWidget): Main widget.
            parent (QWidget, optional): Parent widget.
    """

    def __init__(self, window, parser, movetocenter=True, parent=None):
        QWidget.__init__(self, parent)
        
        self.section_name = "DEFAULT"

        self.parser = parser
        self.parser.read(os.environ['RMQ_COMMON_INI_FILE'])

        self.window = window

        self.setupUi()
        #self.setupEvents(w)
        
        contentLayout = QHBoxLayout()
        contentLayout.setContentsMargins(0, 0, 0, 0)
        
        contentLayout.addWidget(self.window)

        self.windowContent.setLayout(contentLayout)

        self.setWindowTitle(self.window.windowTitle())

        self.setWindowIcon(QIcon("resources/images/rabbit_icon_16.png"))
        self.setGeometry(self.window.geometry())

        self.placescreen(2 if movetocenter else 6)

        
    def setupUi(self):
        
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # create title bar, content
        self.vboxWindow = QVBoxLayout(self)
        self.vboxWindow.setContentsMargins(0, 0, 0, 0)
        
        self.windowFrame = QWidget(self)
        self.windowFrame.setObjectName('windowFrame')

        self.vboxFrame = QVBoxLayout(self.windowFrame)
        self.vboxFrame.setContentsMargins(0, 0, 0, 0)
        
        self.titleBar = WindowDragger(self, self.windowFrame)
        self.titleBar.setObjectName('titleBar')
        self.titleBar.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,
                                                QSizePolicy.Fixed))
        self.hboxTitle = QHBoxLayout(self.titleBar)
        self.hboxTitle.setContentsMargins(0, 0, 0, 0)
        
        #self.hboxTitle.setSpacing(0)
        
        self.btnClose = QToolButton(self.titleBar)
        self.btnClose.setObjectName('btnClose')
        self.btnClose.setSizePolicy(size_policy)
        self.hboxTitle.addWidget(self.btnClose)

        self.btnMinimize = QToolButton(self.titleBar)
        self.btnMinimize.setObjectName('btnMinimize')
        self.btnMinimize.setSizePolicy(size_policy)
        self.hboxTitle.addWidget(self.btnMinimize)

        #self.btnMinimize.setVisible(False)

        self.btnRestore = QToolButton(self.titleBar)
        self.btnRestore.setObjectName('btnRestore')
        self.btnRestore.setSizePolicy(size_policy)
        self.hboxTitle.addWidget(self.btnRestore)

        self.btnRestore.setVisible(False)

        self.btnMaximize = QToolButton(self.titleBar)
        self.btnMaximize.setObjectName('btnMaximize')
        self.btnMaximize.setSizePolicy(size_policy)
        self.hboxTitle.addWidget(self.btnMaximize)
        
        # self.btnMaximize.setVisible(False)

        self.showbuttons()
       
        self.spacelabel = QLabel("|")  #dummy label for space
        self.spacelabel.setSizePolicy(size_policy)
        self.hboxTitle.addWidget(self.spacelabel)

        QPixmapCache.clear()
        self.lblIcon = QLabel()
        self.pixmap = QPixmap("resources/images/rabbit_icon_16.png")
        self.lblIcon.setPixmap(self.pixmap)
        self.lblIcon.setSizePolicy(size_policy)
        self.hboxTitle.addWidget(self.lblIcon)

        #self.spacelabel = QLabel()  #dummy label for space
        #self.spacelabel.setSizePolicy(size_policy)
        #self.hboxTitle.addWidget(self.spacelabel)
        
        self.lblTitle = QLabel('Title')
        self.lblTitle.setObjectName('lblTitle')
        #self.lblTitle.setAlignment(Qt.AlignCenter)        
        self.hboxTitle.addWidget(self.lblTitle)

        self.versionlabel = QLabel()  
        self.versionlabel.setText("Version - {version}".format(version=self.parser.get(self.section_name, 'app.version')))
        #self.spacelabel.setSizePolicy(size_policy)
        self.versionlabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.hboxTitle.addWidget(self.versionlabel)

        self.vboxFrame.addWidget(self.titleBar)

        self.windowContent = QWidget(self.windowFrame)
        self.vboxFrame.addWidget(self.windowContent)

        self.vboxWindow.addWidget(self.windowFrame)

        # set window flags
        #self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.Tool)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        self.window.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        '''Qt::CustomizeWindowHint 
        | Qt::WindowTitleHint | Qt: 
        | Qt::WindowCloseButtonHint | Qt::WindowMaximizeButtonHint'''       

        if QT_VERSION >= (5,):
            self.setAttribute(Qt.WA_TranslucentBackground)

        # set stylesheet
        with open(_FL_STYLESHEET) as stylesheet:
            self.setStyleSheet(stylesheet.read())

        # automatically connect slots
        QMetaObject.connectSlotsByName(self)

    def placescreen(self, pos):
        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width() / pos) - (self.frameSize().width() / pos),
                  (resolution.height() / pos) - (self.frameSize().height() / pos)) 

    def setWindowTitle(self, title):
        self.lblTitle.setText(title)

    '''
    def setupEvents(self, w):
        w.close = self.close
        self.closeEvent = w.closeEvent
    '''

    @Slot()
    def on_btnMinimize_clicked(self):
        self.setWindowState(Qt.WindowMinimized)

    @Slot()
    def on_btnRestore_clicked(self):
        self.btnRestore.setVisible(False)
        self.btnMaximize.setVisible(True)

        self.setWindowState(Qt.WindowNoState)

    @Slot()
    def on_btnMaximize_clicked(self):
        self.btnRestore.setVisible(True)
        self.btnMaximize.setVisible(False)

        self.setWindowState(Qt.WindowMaximized)
    
    '''
    @Slot()
    def on_titleBar_doubleClicked(self):
        if self.btnMaximize.isVisible():
            self.on_btnMaximize_clicked()
        else:
            self.on_btnRestore_clicked()
    '''
    
    @Slot()
    def on_btnClose_clicked(self):
        self.close()

        if self.window is not None:
            self.window.close()

    def closeEvent(self, event):
        self.close()

        if self.window is not None:
            self.window.close()
        
        event.accept()

    def showbuttons(self):
        
        showminButton = self.parser.get(self.section_name, 'show.minimize.button')
        showmaxButton = self.parser.get(self.section_name, 'show.maximize.button')

        self.btnMinimize.setVisible(False if showminButton in ("false", "") else True)
        self.btnMaximize.setVisible(False if showmaxButton in ("false", "") else True)