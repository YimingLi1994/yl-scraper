import json
import socketserver


def recvall(sock, buffer_size=1024):
    buf = sock.recv(buffer_size).decode('ascii', 'ignore')
    while buf:
        yield buf
        buf = sock.recv(buffer_size).decode('ascii', 'ignore')


def recv_basic(the_socket):
    data = ''.join(recvall(the_socket))
    return data.strip()


class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        self.request.settimeout(2)
        self.data = recv_basic(self.request)
        # self.data = self.request.recv(8192).strip().decode('ascii', 'ignore')
        # print(self.data)
        httplst = self.data.split(' ')
        if httplst[0] == 'POST' and len(httplst) >= 3:
            # print('>>>>>>>>>>>>>res uploaded')
            if httplst[1] == '/?key={}'.format(self.server.recv_key):
                pos = len('''POST /?key={} '''.format(self.server.recv_key))
                retload = self.data[pos:]
                payload_all = json.loads(retload)
                with self.server.ret_lock:
                    self.server.ret_dict[payload_all['ret']['DISTRIBUTED_ID']] = payload_all['ret']
                with self.server.crawl_lock:
                    self.server.crawl_val.value += 1
                    # tempnum=self.server.crawl_val.value
                    # print(tempnum)


def server_receiver(port, key, value, val_lock, ret_dict, ret_lock):
    HOST = ''
    server = socketserver.TCPServer((HOST, port), MyTCPHandler)
    server.recv_key = key
    server.ret_dict = ret_dict
    server.ret_lock = ret_lock
    server.crawl_val = value
    server.crawl_lock = val_lock
    server.serve_forever()


    # conn = MySQLdb.connect(host='127.0.0.1', port='22222', user='root', passwd='jxiao0', db='scraper')
    # Create the server, binding to localhost on port 9999
