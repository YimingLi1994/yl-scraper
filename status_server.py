import socketserver
import json
import datetime as dt, pytz
import uuid

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        self.request.settimeout(10)
        self.data = self.request.recv(1024).strip().decode('ascii', 'ignore')
        #print(self.data)
        #print(self.data)
        httplst = self.data.split(' ')
        if httplst[0] == 'GET' and len(httplst) >= 2:

            if self.server.status_key in httplst[1]:
                status_dict={'waitDict':len(self.server.waitDict),
                             'retDict':len(self.server.retDict),
                             'counter':self.server.counter.value,
                             'speed':self.server.speed_counter['speed'],
                             'job_queue' : self.server.job_queue.qsize(),
                            'upload_queue' : self.server.upload_queue.qsize(),
                             }
                retstr = 'HTTP/1.1 200 OK\n\n' + str(json.dumps(status_dict))
                retstr = retstr.encode('ascii')
                self.request.sendall(retstr)


def status_server(port, waitDict, retDict, counter, speed_counter, job_queue, upload_queue, status_key):
    server = socketserver.TCPServer(('', port), MyTCPHandler)
    server.waitDict = waitDict
    server.retDict = retDict
    server.counter = counter
    server.speed_counter = speed_counter
    server.job_queue = job_queue
    server.upload_queue = upload_queue
    server.status_key = status_key
    server.serve_forever()
