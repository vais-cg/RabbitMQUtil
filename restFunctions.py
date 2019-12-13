import os

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from forcediphttpsadapter.adapters import ForcedIPHTTPSAdapter

from messagebox import MessageBox

class RestFunctions:
    
    def __init__(self):
        RestFunctions.__init__(self)

    def get_data(session, url, user, userPass, certificateName):
        print("{nl}URL: {url}{nl1}".format(nl=os.linesep, url=url, nl1=os.linesep))

        isSecureURL = True

        #print(url, user, userPass, certificateName)
        try:
            if len(certificateName.strip()) == 0:
                isSecureURL = False
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
            else:    
                session.mount('https://' , ForcedIPHTTPSAdapter())     
                    
            headers = {
                    'content-type': 'application/x-www-form-urlencoded,application/json,text/html',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Cache-Control': 'max-age=0',
                    'Connection': 'keep-alive'
                    }

            if isSecureURL:
                response = session.get(url,  auth=(user, userPass), headers=headers,  timeout=5, verify=certificateName)
            else:
                response = session.get(url,  auth=(user, userPass), headers=headers,  timeout=5, verify=False)

            response.raise_for_status()
            items = response.json()
            response = {} 
            return items
        except Exception as e:
            MessageBox.message(QMessageBox.Critical, "RabbitMQ REST Connection - Error", "REST API Error", "Unable to retreive data: {}".format(str(e))) 
            return {}    

    def post_data(session, url, user, userPass, certificateName, body):
        print("{nl}URL: {url}{nl1}".format(nl=os.linesep, url=url, nl1=os.linesep))
        
        isSecureURL = True

        try:
            if len(certificateName.strip()) == 0:
                isSecureURL = False
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
            else:    
                session.mount('https://' , ForcedIPHTTPSAdapter())     
            
            if isSecureURL:
                response = session.post(url,  auth=(user, userPass), verify=certificateName, json=body)
            else:
                response = session.post(url,  auth=(user, userPass), verify=False, json=body)

            response.raise_for_status()
            items = response.json()
            response = {} 
            return items 
        except Exception as e:
            MessageBox.message(QMessageBox.Critical, "RabbitMQ REST Connection - Error", "REST API Error", "Unable to retreive data: {}".format(str(e))) 
            return {}          

    def exchange_list(self, parent, sessionAvailable, session, url, user, userPass, certName):
        if sessionAvailable:
            #print('{nl}---------------- Exchange List ---------------------------{nl1}'.format(nl=os.linesep, nl1=os.linesep))
            elisturl = ('{url}api/exchanges').format(url=url)

            #parent.statusBar.showMessage(elisturl)

            self.items = self.get_data(session, elisturl, user, userPass, certName)
            
            #parent.exchange_list.clear()
           
            return self.items 

    def queue_list(self, parent, sessionAvailable, session, url, user, userPass, certName):
        if sessionAvailable:
            #print('{nl}---------------- Queue List ---------------------------{nl1}'.format(nl=os.linesep, nl1=os.linesep))
            qlisturl = '{url}api/queues'.format(url=url)          

            #parent.statusBar.showMessage(qlisturl)

            self.items = self.get_data(session, qlisturl, user, userPass, certName)    
            
            #parent.queue_list.clear()

            return self.items

    def selectedExchangeList(self, parent, session, url, exchangeName, user, userPass, certName):
        #print("Selected Exchange: ", self.exchange_list.currentItem().text())

        parent.queue_list.clearSelection()

        data = self.exchange_bindings(self, parent, session, url, exchangeName, user, userPass, certName)               

        #print(data)

        dummyData = []
        parent.messagetablemodelview.model().changeData(dummyData)

        dummyData1 = []
        parent.bindingtablemodelview.model().changeData(dummyData1)

        '''
        rowid = 0
        for d in data:
            parent.bindingtablemodelview.model().update(rowid, d)          
            rowid = rowid + 1
        '''

        parent.bindingtablemodelview.model().changeData(data)          

        parent.bindingtablemodelview.model().backupData()

        parent.numEQRecs.setText(str(parent.bindingtablemodelview.model().rowCount()))

    def selectedQueueList(self, parent, session, url, queueName, user, userPass, certName):
        #print("Selected Queue: ", self.queue_list.currentItem().text())

        parent.exchange_list.clearSelection()

        data = self.queue_bindings(self, parent, session, url, queueName, user, userPass, certName)

        #print(data)

        dummyData = []
        parent.messagetablemodelview.model().changeData(dummyData)

        dummyData1 = []
        parent.bindingtablemodelview.model().changeData(dummyData1)

        '''
        rowid = 0
        for d in data:
            parent.bindingtablemodelview.model().update(rowid, d)          
            rowid = rowid + 1
        '''

        parent.bindingtablemodelview.model().changeData(data)

        parent.bindingtablemodelview.model().backupData()

        parent.numEQRecs.setText(str(parent.bindingtablemodelview.model().rowCount()))    


    def _exchange_detail(self, session, url, exchange_name, user, userPass, certName):
        #print('{nl}---------------- Exchange Detail ---------------------------{nl1}'.format(nl=os.linesep, nl1=os.linesep))
        eurl = ('{url}api/exchanges/{vhost}/{exchg_name}').format(url=url, vhost='%2F', exchg_name=exchange_name )            

        self.items = {}
        self.items = self.get_data(session, eurl, user, userPass, certName)          
        
        return self.items


    def exchange_bindings(self, parent, session, url, exchange_name, user, userPass, certName):
        #print('{nl}---------------- Exchange Detail ---------------------------{nl1}'.format(nl=os.linesep, nl1=os.linesep))
        eurl = ('{url}api/exchanges/{vhost}/{exchg_name}/bindings/source').format(url=url, vhost='%2F', exchg_name=exchange_name )            

        #parent.statusBar.showMessage(eurl)

        self.eitems = self._exchange_detail(self, session, url, exchange_name, user, userPass, certName)       
        
        self.items = self.get_data(session, eurl, user, userPass, certName)   

        self.filteredItems = []

        row = 1
        for item in self.items:
            arrItems = []

            arrItems.append(row)
            arrItems.append(item["source"]) 
            arrItems.append(self.eitems["type"]) 
            arrItems.append(self.eitems["auto_delete"])
            arrItems.append(item["destination"])
            arrItems.append(item["destination_type"])
            arrItems.append(item["routing_key"])
            
            msgArguments = ""            
            arguments = item["arguments"]

            for k, v in arguments.items():                    
                msgArguments = msgArguments + "{key}:{val},".format(key=k, val=v)
            
            arrItems.append(msgArguments[:-1].strip())
                        
            arrItems.append(item["properties_key"])

            arrItems.append(arguments)

            self.filteredItems.append(arrItems)

            row = row + 1
        
        return self.filteredItems

    def queue_bindings(self, parent, session, url, queue_name, user, userPass, certName):
        #print('{nl}---------------- Exchange Detail ---------------------------{nl1}'.format(nl=os.linesep, nl1=os.linesep))
        eurl = ('{url}api/queues/{vhost}/{queue_name}/bindings').format(url=url, vhost='%2F', queue_name=queue_name )            
        
        #parent.statusBar.showMessage(eurl)

        self.items = {}
        self.items = self.get_data(session, eurl, user, userPass, certName)   

        self.filteredItems = []
        
        row = 1
        for item in self.items:
            arrItems = []

            source = item["source"]
            destination = item["destination"]
            routing_key = item["routing_key"]

            if source != "" and destination != routing_key:
                arrItems.append(row)
                arrItems.append(source) 
                arrItems.append("") 
                arrItems.append("") 
                arrItems.append(destination)
                arrItems.append(item["destination_type"])
                arrItems.append(routing_key)
                
                msgArguments = ""            
                arguments = item["arguments"]

                for k, v in arguments.items():                    
                    msgArguments = msgArguments + "{key}:{val},".format(key=k, val=v)
                
                arrItems.append(msgArguments[:-1].strip())

                arrItems.append(item["properties_key"])

                arrItems.append(arguments)
                
                self.filteredItems.append(arrItems)

                row = row + 1

        return self.filteredItems

    def queue_messages(self, parent, sessionAvailable, session, url, queue_name, user, userPass, certName):
        if sessionAvailable:
            #print('{nl}---------------- Queue Detail ---------------------------{nl1}'.format(nl=os.linesep, nl1=os.linesep))
            qurl = '{url}api/queues/{vhost}/{qname}/get'.format(url=url, vhost='%2F', qname=queue_name)            
            
            parent.statusBar.showMessage(qurl)

            '''
            ackmode = ack_requeue_false    <-- Ack Message, requeue False
            ackmode = ack_requeue_true     <-- Nack Message, requeue true
            ackmode = reject_requeue_false <- Reject message, requeue false
            ackmode = reject_requeue_true  <-- Reject message, requeue true
            '''
            self.body = {
                        'count':'5000', 
                        'requeue':'true',
                        'encoding':'auto',
                        'ackmode':'ack_requeue_true'
                   } 
            
            #Data is returned in the following order and we are reordering it
            #  "Payload Bytes", "Redelivered", "Exchange", "Routing Key", "Message Count", "Properties", "Payload", "Payload Encoding"
            self.items = self.post_data(session, qurl, user, userPass, certName, self.body)

            self.filteredItems = []                       
            
            row = 1
            for item in self.items:
                arrItems = []
                basicProperties=""
                messageHeaders=""

                arrItems.append(row)
                arrItems.append(item["exchange"]) 
                arrItems.append(item["routing_key"])
                arrItems.append(item["payload_bytes"])
                arrItems.append(item["redelivered"])

                properties = item["properties"]

                for k, v in properties.items():                    
                    if k != "headers":
                        basicProperties = basicProperties + "{nl}{key}:{val}".format(nl=os.linesep, key=k, val=v)
                    else:
                        for x, y in v.items():
                            messageHeaders = messageHeaders  + "{nl}{key}:{val}".format(nl=os.linesep, key=x, val=y)                


                arrItems.append(basicProperties)
                arrItems.append(messageHeaders)               

                message = item["payload"]
                
                #os.linesep.join(message.splitlines()) 
                #message = message.replace(r'\r\n', os.linesep)      

                arrItems.append(message)

                arrItems.append(properties)

                self.filteredItems.append(arrItems)

                row = row + 1
         
            return self.filteredItems

    def vhosts(self, parent, sessionAvailable, session, url, user, userPass, certName):
        if sessionAvailable:            
            #print('{nl}---------------- Exchange Detail ---------------------------{nl1}'.format(nl=os.linesep, nl1=os.linesep))
            eurl = ('{url}api/vhosts').format(url=url)
        
            #parent.statusBar.showMessage(eurl)

            self.items = {}
            self.items = self.get_data(session, eurl, user, userPass, certName)   

            self.filteredItems = []            

            row = 1
            for item in self.items:
                arrItems = []

                arrItems.append(row)
                arrItems.append(item["name"]) 

                self.filteredItems.append(arrItems)

                row = row + 1         
            
            return self.filteredItems


    def nodes(self, parent, sessionAvailable, session, url, user, userPass, certName):
        if sessionAvailable:            
            #print('{nl}---------------- Exchange Detail ---------------------------{nl1}'.format(nl=os.linesep, nl1=os.linesep))
            eurl = ('{url}api/nodes').format(url=url)
        
            #parent.statusBar.showMessage(eurl)

            self.items = {}
            self.items = self.get_data(session, eurl, user, userPass, certName)             
            
            return self.items

        