from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import json

import uuid

import pika

import os

from messagebox import MessageBox

class ImportMessages:

    def __init__(self):
        super(ImportMessages, self).__init__()       
           
    def getFileForImport(parent):
        options = QFileDialog.Options()
        #options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(parent,"Select a file to import message(s)", ".","JSON Files (*.json);; All Files(*.*)", options=options)
        data = None
        if fileName:   
            data = json.load(open(fileName))
        return data

    def shovelMessages(self, exchange, routingKey, props, msgdata, sessionAvailable, amqpConnection, textContents):
        if sessionAvailable:
            #print("Importing...")             

            if not exchange:
                MessageBox.message(QMessageBox.Warning, "RabbitMQ Shovel Message", "Missing Input!", "Please select an exchange")
                return
            
            if not routingKey or not props:
                MessageBox.message(QMessageBox.Warning, "RabbitMQ Shovel Message", "Missing Input!", "Please select a Routing Key or provide properties or headers.")
                return

            if amqpConnection is None:
                MessageBox.message(QMessageBox.Warning, "RabbitMQ Shovel Message", "AMQP Connection Error!", "AMQP connection is not available.{nl}Please check".format(nl=os.linesep))
                return

            channel = amqpConnection.channel()

            #print(msgdata)

            #messages =  json.loads(json.dumps(msgdata))
            messages =  json.loads(msgdata)

            #print(messages)

            for key in messages:                    
                
                #print(messages[key])
        
                if "message_" not in key:
                    MessageBox.message(QMessageBox.Warning, "RabbitMQ Shovel Message", "Message Shoveling Error!", "Key should contain ""message_*"" where * indicates message number.{nl}Please check".format(nl=os.linesep))
                    return

                message = messages[key]['body']
                
                hasMessageId = False

                if props != {}:
                    if not hasMessageId:
                        hasMessageId = props.get('message_id') is not None

                    if not hasMessageId:
                        print("Adding message_id ...")    
                        props['message_id'] = uuid.uuid4().hex

                    if props.get('content_type') is None:
                        print("Adding content_type ...")    
                        props['content_type'] = "application/json"
               
                #print(message, props)

                properties = pika.BasicProperties()                   

                for pKey in props:
                    if props.get(pKey) is not None:
                        setattr(properties, pKey, props.get(pKey))                        
                    print(pKey, props.get(pKey))

                #print(properties)

                if len(routingKey.strip()) == 0:
                        routingKey = ""

                try:                        
                    #channel.confirm_delivery()

                    exch_exist = channel.exchange_declare(exchange=exchange, passive=True)

                    if exch_exist:
                        channel.basic_publish(exchange=exchange, routing_key=routingKey, body=message, properties=properties)

                        MessageBox.message(QMessageBox.Information, "RabbitMQ Shovel Message", "Message Copied!", \
                                               "Message published to Exchange: {exch}.".format(exch=exchange))
                    else:
                        MessageBox.message(QMessageBox.Warning, "RabbitMQ Shovel Message", "Exchange Does not exist!", 
                                                      "Exchange:{exch} aldoes not exists.".format(exch=exchange))                             
                except Exception as e:            
                    error = str(e).strip().replace("(", "").replace(")", "").split(",")
                    textandinfo = error[1].replace("\"","").split("-")
                    text = textandinfo[0].replace("\"","").strip()
                    infoText = textandinfo[1].replace("\"","").strip()    
                    MessageBox.message(QMessageBox.Critical, "RabbitMQ Shovel Message - Error ({})".format(error[0]), text, infoText)  
                        

            if channel.is_open:
                channel.close()

            #self._refresh.emit(True)    
        
    def importMessages(self, parent, sessionAvailable, amqpConnection):
        if sessionAvailable:
            #print("Importing...")             

            fileData = self.getFileForImport(parent)
            
            if fileData is not None:
                
                #print(amqpConnection)          
                
                if amqpConnection is None:
                    MessageBox.message(QMessageBox.Warning, "RabbitMQ Import Message", "AMQP Connection Error!", "AMQP connection is not available.{nl}Please check".format(nl=os.linesep))
                    return

                channel = amqpConnection.channel()

                for key in fileData:                    
                    #print(fileData[key])
                    if "message_" not in key:
                        MessageBox.message(QMessageBox.Warning, "RabbitMQ Import Message", "Import Error!", "Invalid JSON file.{nl}Please check".format(nl=os.linesep))
                        return

                    exchange = fileData[key]['exchange']
                    routingKey = fileData[key]['routing_key']     
                    message = fileData[key]['body']
                    props = fileData[key]['properties']
                    
                    headers = {}

                    if props.get('headers') is not None:
                        headers = props['headers']                    
                   
                    hasMessageId = False

                    if headers != {}:
                        if not hasMessageId:
                            hasMessageId = headers.get('JMSMessageID') is not None

                        if not hasMessageId:
                            hasMessageId = headers.get('message_id') is not None

                        if not hasMessageId:
                            hasMessageId = headers.get('msg_id') is not None

                    if props != {}:
                        if not hasMessageId:
                            hasMessageId = props.get('message_id') is not None

                        if not hasMessageId:
                            print("Adding message_id ...")    
                            props['message_id'] = uuid.uuid4().hex

                        if props.get('content_type') is None:
                            print("Adding content_type ...")    
                            props['content_type'] = "application/json"

                    #print(exchange, routingKey, message, props)

                    properties = pika.BasicProperties()                   

                    for pKey in props:
                        if props.get(pKey) is not None:
                           setattr(properties, pKey, props.get(pKey))                        
                        #print(pKey, props.get(pKey))

                    #print(properties)
                    
                    if len(routingKey.strip()) == 0:
                        routingKey = ""

                    try:                        
                        #channel.confirm_delivery()
                        exch_exist = channel.exchange_declare(exchange=exchange, passive=True)

                        #print("exch_exist: {}".format(exch_exist))

                        if exch_exist:
                            channel.basic_publish(exchange=exchange, routing_key=routingKey, body=message, properties=properties)

                            MessageBox.message(QMessageBox.Information, "RabbitMQ Import Message", "Message Imported!", \
                                               "Message published to Exchange: {exch}.".format(exch=exchange))
                        else:
                            MessageBox.message(QMessageBox.Warning, "RabbitMQ Import Message", "Exchange Does not exist!", 
                                                      "Exchange:{exch} aldoes not exists.".format(exch=exchange))                                                                       
                    except Exception as e:            
                        error = str(e).strip().replace("(", "").replace(")", "").split(",")
                        textandinfo = error[1].replace("\"","").split("-")
                        text = textandinfo[0].replace("\"","").strip()
                        infoText = textandinfo[1].replace("\"","").strip()    
                        MessageBox.message(QMessageBox.Critical, "RabbitMQ Import Message - Error ({})".format(error[0]), text, infoText)  
                        

                if channel.is_open:
                    channel.close()

                #parent.refresh()        
