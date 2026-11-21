import socket

hostName='example.com'
port = 80

s = socket.socket()
#s.settimeout(10)
s.connect((hostName,port))

print(f"Connect to : {s.getpeername()}")

request = f"GET / HTTP/1.1\r\nHost: {hostName}\r\nConnection: close\r\n\r\n"
s.sendall(request.encode("utf-8"))

response = b""
while True:
    chunk = s.recv(4096)
    if not chunk:
        break
    response += chunk

# print(response.decode("utf-8", errors="replace"))

def get_html():
  return response

s.close()

