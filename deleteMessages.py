import json

import pika

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from messagebox import MessageBox

class DeleteMessages:
    
    def __init__(self):
        DeleteMessages.__init__(self)      

    def deleteMessages(self, queue, msgdataToBeDeleted, sessionAvailable, amqpConnection, allOthers):
        if sessionAvailable:
            #print("Deleting...")             

            if amqpConnection is None:
                MessageBox.message(QMessageBox.Warning, "RabbitMQ Delete Message", "AMQP Connection Error!", "AMQP connection is not available.{nl}Please check".format(nl=os.linesep))
                return

            print(amqpConnection)
            
            channel = amqpConnection.channel()            

            messagesToBeDeleted =  json.loads(msgdataToBeDeleted)

            messagesToBeNAcked =  json.loads(allOthers)

            #print(messagesToBeDeleted, messagesToBeNAcked)

            tobeNAckedMessages = []
            for key in messagesToBeNAcked:
                #print("nack:{}".format(key))
                message = messagesToBeNAcked[key]['body']
                tobeNAckedMessages.append(message)
            
            tobeDeletedMessages = []
            for key in messagesToBeDeleted:
                #print("rej:{}".format(key))
                message = messagesToBeDeleted[key]['body']
                tobeDeletedMessages.append(message)

            encoding = 'utf-8'

            message_delete_count = 0

            # Get ten messages and break out
            for method_frame, properties, body in channel.consume(queue):

                # Display the message parts
                #print(properties)

                #print(method_frame, body, type(body), tobeNAckedMessages, tobeDeletedMessages)

                '''if str(body, encoding) in tobeNAckedMessages:
                    # NAck the message and set requeue to True, so the message gets requeued
                    print(method_frame, body, tobeNAckedMessages, tobeDeletedMessages)
                    channel.basic_nack(method_frame.delivery_tag, requeue=True)'''

                if str(body, encoding) in tobeDeletedMessages:
                    # Reject the message and set requeue to False, so the message gets deleted
                    #print(method_frame, body, tobeNAckedMessages, tobeDeletedMessages)
                    
                    channel.basic_reject(method_frame.delivery_tag, requeue=False)                   
                    #print("Message with delivery tag:{tag} deleted.".format(tag=method_frame.delivery_tag))
                    MessageBox.message(QMessageBox.Information, "RabbitMQ Delete Message", "Message Deleted!", \
                                               "Message with delivery tag:{tag} deleted.".format(tag=method_frame.delivery_tag))
                    message_delete_count = message_delete_count + 1


                if message_delete_count == len(tobeDeletedMessages):
                    # Cancel the consumer and return any pending messages
                    requeued_messages = channel.cancel()
                    #print('Requeued %i messages' % requeued_messages)

            channel.close()  
