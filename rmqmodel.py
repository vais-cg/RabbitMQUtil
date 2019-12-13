from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtGui import QIcon, QColor

import operator

class TableModel(QAbstractTableModel):

    def __init__(self, datain, headerdata = [], parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain
        self.headerdata = headerdata
        self.parent = parent       

        self.name = ""

    def setName(self, name):
        self.name = name
    
    def rowCount(self, parent=QModelIndex()):         
        return len(self.arraydata) 
 
    def columnCount(self, parent=QModelIndex()):     
        if self.headerdata:                
            columns = len(self.headerdata)
   
            if columns > 0:
                return columns
            else: 
                return 0     

    def data(self, index, role=Qt.EditRole):
        try:                
            if not index.isValid(): 
                return QVariant() 
            elif role != Qt.DisplayRole: 
                return QVariant() 
        
            return QVariant(self.arraydata[index.row()][index.column()])     
        except:
            pass        
 
    def setData(self, index, value, role = Qt.EditRole):
        row = index.row()
        column = index.column()

        #print(role)
        
        if role == Qt.EditRole:
            if self.columnCount() == 2:
                
                if column == 0:
                    (self.arraydata[row])[column] = value
                elif column == 1:
                    (self.arraydata[row]).append(value)
                
                #print(self.arraydata)

                self.dataChanged.emit(index, index)
                return True       

        return False

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            #print(col)
            return self.headerdata[col]
        return None    
    
    def flags(self, index):
        if not index.isValid():
            return None
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable 

    
    def update(self, rownum, data):
        self.beginResetModel() 
        
        if self.rowCount(self.parent) == rownum:
            self.arraydata.insert(rownum, data)
        else:
            if self.columnCount() == 2:
                self.arraydata[rownum][0] = data[0]
                self.arraydata[rownum][1] = data[1]
        
        self.endResetModel()

    def changeData(self, datain):
        self.beginResetModel() 
        self.arraydata = datain        
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))        
        self.endResetModel()

    def sort(self, col, order):
        """sort table by given column number col"""
        # print(">>> sort() col = ", col)
        self.layoutAboutToBeChanged.emit()
        self.arraydata = sorted(self.arraydata, key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.arraydata.reverse()
        self.layoutChanged.emit()    

    def backupData(self):
        self.originaldata = self.arraydata

    def setFilter(self, searchText):       
              
        filteredData = []           
        
        if len(searchText) > 0:
            for item in self.arraydata:                
                result = (searchText in str(item))
                if result:
                    filteredData.append(item)

            self.changeData(filteredData)
        else:
            self.changeData(self.originaldata)

    def removeRowsWithEmptyColumns(self):
        index = -1
        self.beginResetModel()
        for item in self.arraydata:   
            index = index + 1            
            if len(item) == 2:
                if item[0] == [] or len(item[0]) == 0:
                    del self.arraydata[index]
        self.endResetModel()        

    #Row shifting
    def dropMimeData(self, data, action, row, col, parent):
        """
        Always move the entire row, and don't allow column "shifting"
        """
        return super().dropMimeData(data, action, row, 0, parent)

        
