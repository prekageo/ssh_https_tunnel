import socket
import select
import time

proxy_addr = ('10.1.1.1', 8080)
ssh_tunnel_remote = ('1.2.3.4', 443)

def obfuscate(data):
  return ''.join(chr(ord(x)^0x42) for x in data)

class RateLimiter:
  def __init__(self, max_rate):
    self.max_rate = max_rate
    self.last_send = 0
    self.available = max_rate

  def on_data_received(self, length):
    this_send = time.time()
    self.available = min(self.max_rate, int(self.available + self.max_rate * (this_send-self.last_send)))
    #print this_send,length,self.available,
    if self.available >= length:
      self.available -= length
      #print 'go',self.available
    else:
      delay = 1.0*(length-self.available)/self.max_rate
      #print 'delay',delay
      time.sleep(delay)
      this_send += delay
      self.available = 0
    self.last_send = this_send

local_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_server.bind(('127.0.0.1',900))
local_server.listen(1)
while 1:
  local, addr = local_server.accept()
  print 'Connected by', addr
  remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  remote.connect(proxy_addr)
  remote.sendall('CONNECT %s:%d HTTP/1.1\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.1; rv:16.0) Gecko/20100101 Firefox/16.0\r\nProxy-Connection: keep-alive\r\nHost: %s\r\n\r\n' % (ssh_tunnel_remote[0], ssh_tunnel_remote[1], ssh_tunnel_remote[0]))
  data = remote.recv(1024)
  assert data == 'HTTP/1.0 200 Connection established\r\n\r\n', data
  print 'connection established'
  inbound = 0
  outbound = 0
  total = 0
  limiter = RateLimiter(2048)
  start_time = time.time()
  while 1:
    ready,_,_ = select.select([remote, local], [], [])
    if remote in ready:
      data = remote.recv(1024)
      if data:
        limiter.on_data_received(len(data))
        inbound += len(data)
        data = obfuscate(data)
        local.sendall(data)
      else:
        print 'remote closed connection'
        break
    if local in ready:
      data = local.recv(1024)
      if data:
        limiter.on_data_received(len(data))
        outbound += len(data)
        data = obfuscate(data)
        remote.sendall(data)
      else:
        print 'local closed connection'
        break
    if inbound+outbound > total + 100000:
      total = inbound+outbound
      print 'inbound: %d KB, outbound: %d KB, average rate: %d b/s' % (inbound/1024, outbound/1024, total/(time.time()-start_time))
  local.close()
  remote.close()
