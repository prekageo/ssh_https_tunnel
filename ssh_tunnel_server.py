import socket
import select
import sys

def obfuscate(data):
  return ''.join(chr(ord(x)^0x42) for x in data)

remote_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
remote_server.bind(('0.0.0.0',443))
remote_server.listen(1)
while 1:
  remote, addr = remote_server.accept()
  print 'Connected by', addr
  local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  local.connect(('127.0.0.1',22))
  while 1:
    ready,_,_ = select.select([remote, local], [], [])
    if remote in ready:
      data = remote.recv(1024)
      if data:
        #print 'R->L: %d' % len(data)
        data = obfuscate(data)
        local.sendall(data)
      else:
        print 'remote closed connection'
        break
    if local in ready:
      data = local.recv(1024)
      if data:
        #print 'L->R: %d' % len(data)
        data = obfuscate(data)
        remote.sendall(data)
      else:
        print 'local closed connection'
        break
  local.close()
  remote.close()
