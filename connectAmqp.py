from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

import pika

import ssl

from messagebox import MessageBox

class RabbitMQPikaConnection:    

    def __init__(self):
        RabbitMQPikaConnection.__init__(self)

    def connect(self, parent, commandUrl, userName, userPass, certName, vhost, connectionName=''):
        credentials = pika.PlainCredentials(username=userName, password=userPass)

        _commandUrl = commandUrl.split(":")

        #print(commandUrl)
        serverCN = _commandUrl[1].replace("//","")
        commandPort = _commandUrl[2]

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        #ssl_context.verify_mode = ssl.CERT_REQUIRED    
        ssl_context.load_verify_locations(certName)

        ssl_options = pika.SSLOptions(context=ssl_context, server_hostname=serverCN)

        parameters = pika.ConnectionParameters(host=serverCN, port=commandPort, virtual_host=vhost,
                                               connection_attempts=5, 
                                               retry_delay=5, 
                                               credentials=credentials, heartbeat=580, 
                                               blocked_connection_timeout=600, 
                                               ssl_options=ssl_options,
                                               client_properties={
                                                    'connection_name': connectionName,
                                               }
                                            ) 
        try:            
            return pika.BlockingConnection(parameters)
        except Exception as e:
            print(str(e))
            MessageBox.message(QMessageBox.Critical, "RabbitMQ AMQP Connection - Error", "AMQP Error", "Unable to connect to RabbitMQ: {}".format(str(e))) 
            return None      
  