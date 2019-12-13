from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal

import json

import uuid

import pika

import os

from messagebox import MessageBox

class ImportConfig:

    _refresh = QtCore.pyqtSignal(bool)

    def __init__(self):
        super(ImportConfig, self).__init__()          
            
    def getFileForImport(parent):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(parent,"Select a file to import configuration", ".","JSON Files (*.json);; All Files(*.*)", options=options)
        data = None
        if fileName:            
            data = json.load(open(fileName))
        return data
        
    def importConfig(self, parent, sessionAvailable, amqpConnection, exchange_list, queue_list):
        if sessionAvailable:
            #print("Importing...")             

            fileData = self.getFileForImport(parent)
            
            if fileData is not None:
                #print(self.connection)          
                if amqpConnection is None:
                    MessageBox.message(QMessageBox.Warning, "RabbitMQ Import Configuration", "AMQP Connection Error!", "AMQP connection is not available.{nl}Please check".format(nl=os.linesep))
                    return

                for vhosts in fileData:                    
                    #print(vhosts)
                    for vh in fileData[vhosts]:
                        vhost = fileData[vhosts][vh]
                    
                        exchanges = vhost["exchanges"]
                        queues = vhost["queues"]
                        bindings = vhost["bindings"]
                
                        #print(exchanges)
                        #print(queues)
                        #print(bindings)

                        channel = amqpConnection.channel()
                        for exchange in exchanges:
                            if exchange not in exchange_list:    
                                exch = exchanges[exchange]

                                etype = exch["type"]
                                durable = exch["durable"]
                                auto_delete = exch["auto_delete"]
                                internal = exch["internal"]
                                arguments = exch["arguments"]

                                try:
                                    channel.exchange_declare(exchange=exchange, exchange_type=etype, durable=durable, auto_delete=auto_delete, internal=internal, arguments=arguments)
                                    
                                    MessageBox.message(QMessageBox.Information, "RabbitMQ Exchange", "Exchange Created!", 
                                                        "Exchange:{exch} of type:{etype} created.".format(exch=exchange, etype=etype))   
                                except Exception as e:
                                    error = str(e).strip().replace("(", "").replace(")", "").split(",")
                                    #print(error)
                                    textandinfo = error[1].replace("\"","").split("-")
                                    text = textandinfo[0].replace("\"","").strip()
                                    infoText = textandinfo[1].replace("\"","").strip()  + ". Check Queue naming policy with your administrator."    
                                    MessageBox.message(QMessageBox.Critical, "RabbitMQ Exchange Creation - Error ({})".format(error[0]), text, infoText) 
                            else:
                                MessageBox.message(QMessageBox.Warning, "RabbitMQ Exchange", "Exchange Exists!", 
                                                      "Exchange:{exch} already exists.".format(exch=exchange))  

                        if channel.is_open:
                            channel.close()

                        channel = amqpConnection.channel()
                        for queue in queues:                            
                            if queue not in queue_list:
                                qu = queues[queue]
                            
                                durable = qu["durable"]
                                auto_delete = qu["auto_delete"]
                                arguments = qu["arguments"]

                                try:    
                                    channel.queue_declare(queue=queue, durable=durable, auto_delete=auto_delete, arguments=arguments)
                                    MessageBox.message(QMessageBox.Information, "RabbitMQ Queue", "Queue Created!", "{que} has been added.".format(que=queue)) 
                                except Exception as e:
                                    error = str(e).strip().replace("(", "").replace(")", "").split(",")
                                    #print(error)
                                    textandinfo = error[1].replace("\"","").split("-")
                                    text = textandinfo[0].replace("\"","").strip()                                        
                                    infoText = textandinfo[1].replace("\"","").strip()  + ". Check Queue naming policy with your administrator."    
                                    MessageBox.message(QMessageBox.Critical, "RabbitMQ Queue Creation - Error ({})".format(error[0]), text, infoText)         
                            else:
                                MessageBox.message(QMessageBox.Warning, "RabbitMQ Create Queue", "Queue Exists!", "Queue:{qu} already exists.".format(qu=queue))         

                        if channel.is_open:
                            channel.close()

                        channel = amqpConnection.channel()
                        for binding in bindings:
                            bind = bindings[binding]

                            source = binding.split("_")[0]
                            destination = bind["destination"]                                 
                            routing_key = bind["routing_key"]                                
                            arguments = bind["arguments"]   
                            destination_type = bind["destination_type"]

                            if destination_type == "exchange":
                                #print("e2e", destination, source, routing_key, arguments)  

                                try:
                                    channel.exchange_bind(destination=destination, source=source, routing_key=routing_key, arguments=arguments)
                                                                 
                                    msg = "Exchange to Exchange binding created.{nl}------------------------------{nl}destination:{destination}{nl}source:{source}{nl}routing_key:{routing_key}{nl}arguments:{arguments}{nl}------------------------------{nl}" \
                                                .format(nl=os.linesep, destination=destination, source=source, routing_key=routing_key, arguments=arguments)

                                    MessageBox.message(QMessageBox.Information, "RabbitMQ Binding", "Exchange to Exchange Binding!", msg)
                                except Exception as e:
                                    error = str(e).strip().replace("(", "").replace(")", "").split(",")
                                    textandinfo = error[1].replace("\"","").split("-")
                                    text = textandinfo[0].replace("\"","").strip()
                                    infoText = textandinfo[1].replace("\"","").strip()  + ". Check Queue naming policy with your administrator."    
                                    MessageBox.message(QMessageBox.Critical, "RabbitMQ Exchange Binding - Error ({})".format(error[0]), text, infoText)     

                            elif destination_type == "queue":
                                #print("q2q", destination, source, routing_key, arguments)
                                
                                try:
                                    channel.queue_bind(queue=destination, exchange=source, routing_key=routing_key, arguments=arguments)

                                    msg = "Exchange to Queue binding created.{nl}------------------------------{nl}queue:{queue}{nl}exchange:{exchange}{nl}routing_key:{routing_key}{nl}arguments:{arguments}{nl}------------------------------{nl}" \
                                                      .format(nl=os.linesep, queue=destination, exchange=source, routing_key=routing_key, arguments=arguments)

                                    MessageBox.message(QMessageBox.Information, "RabbitMQ Binding", "Exchange to Queue Binding!", msg)    
                                except Exception as e:
                                    error = str(e).strip().replace("(", "").replace(")", "").split(",")
                                    textandinfo = error[1].replace("\"","").split("-")
                                    text = textandinfo[0].replace("\"","").strip()
                                    infoText = textandinfo[1].replace("\"","").strip()  + ". Check Queue naming policy with your administrator."    
                                    MessageBox.message(QMessageBox.Critical, "RabbitMQ Queue Binding - Error ({})".format(error[0]), text, infoText)


                        if channel.is_open:
                            channel.close()
