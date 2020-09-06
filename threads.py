import threading
import time
from datetime import datetime 

# Thread class to receive and send messages 
class NodeThread(threading.Thread):
  def __init__(self, node, role):
    threading.Thread.__init__(self)
    self.node = node
    self.role = role

  def run(self, string=''):
    if self.role == 'recv':
      # Bind and listen on the node
      self.node.bind()
      self.node.listen()
      # Accept the connections
      while True:
        conn = self.node.accept()
        request = self.node.receive(conn)
        self.node.parseRequest(request, conn)
        conn.close()

    elif self.role == 'send':
      # Message to be sent
      time_now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
      string = f'Message::{time_now}:{self.node.host}:{self.node.port}:Hello World!'
      for _ in range(4):
        time.sleep(2)
        for seed in self.node.seeds:
          host, port = seed.split(':')
          self.node.connect(host, int(port))
          self.node.send(string)
          self.node.close()

        for peer in self.node.peers:
          host, port = peer.split(':')
          self.node.connect(host, int(port))
          self.node.send(string)
          self.node.close()

    elif self.role == 'live':
      # Send liveliness messages to peers in the nodes
      time_now = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
      string = f'LivenessRequest::{time_now}:{self.node.host}:{self.node.port}'
      while True:
        time.sleep(13)
        for peer in self.peers:
          requests_sent = self.node.peers_live[peer]
          if requests_sent < 3:
            host, port = peer.split(':')
            self.node.connect(host, int(port))
            self.node.send(string)
            self.node.close()
            self.node.peers_live[peer] += 1
          else:
            self.node.reportDeadPeer(peer)