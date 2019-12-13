from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QItemDelegate

class CellDelegate(QItemDelegate):
    def __init__(self):
        QItemDelegate.__init__(self)

    def createEditor(self, parent, option, index):
        column = index.column()
        
        line_edit = QLineEdit(parent)
        return line_edit     
    
    def setModelData(self, editor, model, index):
        index.model().setData(index, editor.text())