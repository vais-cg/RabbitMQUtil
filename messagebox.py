from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QGridLayout, QSpacerItem, QSizePolicy

from PyQt5 import QtGui
from PyQt5.QtGui import QIcon

from PyQt5 import QtCore
from PyQt5.QtCore import QSize

class MessageBox:    

    def __init__(self):
        MessageBox.__init__(self)

    def message(msgType, title, text="", infoText=""):
        msgBox = QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('./resources/images/rabbit_icon.jpg'))

        msgBox.setIcon(msgType)
        msgBox.setText(text)
        msgBox.setInformativeText(infoText)
        msgBox.setWindowTitle(title)
        #msgBox.setDetailedText("Detailed Text")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setEscapeButton(QMessageBox.Ok)       

        horizontalSpacer = QSpacerItem(500, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout = msgBox.layout()
        layout.addItem(horizontalSpacer, layout.rowCount(), 0, 1, layout.columnCount())

        msgBox.exec_()    