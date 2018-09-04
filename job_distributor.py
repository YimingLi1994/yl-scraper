import socketserver
import json
import datetime as dt, pytz
import uuid
import struct

def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        self.request.settimeout(2)
        self.data = self.request.recv(1024).strip().decode('ascii', 'ignore')
        # print(self.data)
        httplst = self.data.split(' ')
        if httplst[0] == 'GET' and len(httplst) >= 2:
            if self.server.crawl_key in httplst[1]:
                if self.server.crawl_queue.empty():
                    retstr = 'HTTP/1.1 200 OK\n\n' + '''thispayload:empty'''
                else:
                    payload = self.server.crawl_queue.get()
                    payload['DISTRIBUTED_TIME'] = dt.datetime.now(pytz.timezone('America/Chicago')).strftime('%Y-%m-%d %H:%M:%S')
                    payload['DISTRIBUTED_ID'] = str(uuid.uuid4())
                    if 'retry' not in payload:
                        payload['retry'] = 0
                    if 'distributed' not in payload:
                        payload['distributed'] = 0
                    payload['distributed'] += 1
                    with self.server.waitlock:
                        self.server.waitDict[payload['DISTRIBUTED_ID']] = payload
                    retstr = 'HTTP/1.1 200 OK\n\n' + 'thispayload:' + str(json.dumps(payload)).strip()
                retstr = retstr.encode('ascii')
                send_msg(self.request, retstr)


def server_distributor(port,key, queue, waitDict, waitLock):
    server = socketserver.TCPServer(('', port), MyTCPHandler)
    server.crawl_key = key
    server.crawl_queue = queue
    server.waitDict = waitDict
    server.waitlock = waitLock
    server.serve_forever()
