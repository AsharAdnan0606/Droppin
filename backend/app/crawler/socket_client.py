import socket
import ssl
import certifi

port = 80

#cuts raw bytes into status code, headers, body
def parse_response(raw):
    head, _, body = raw.partition(b"\r\n\r\n")
    lines = head.decode("iso-8859-1").split("\r\n")

    status_line = lines[0]
    status_code = int(status_line.split(" ", 2)[1])

    headers = {}
    for line in lines[1:]:
        name, _, value = line.partition(":")
        headers[name.strip().lower()] = value.strip()

    return status_code, headers, body


#remove size labels from chunked body
def decode_chunked(body):
    result = b""
    while body:
        size_line, _, body = body.partition(b"\r\n")
        size = int(size_line.split(b";")[0], 16)
        if size == 0:
            break
        result += body[:size]
        body = body[size + 2:]
    return result



def get_html(host, port=443, use_tls=True):
    s = socket.socket()
    s.settimeout(10)
    s.connect((host, port))

    if use_tls:
        context = ssl.create_default_context(cafile=certifi.where())
        s = context.wrap_socket(s, server_hostname=host)

    print(f"Connect to : {s.getpeername()}")

    request = f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
    s.sendall(request.encode("utf-8"))

    response = b""
    while True:
      chunk = s.recv(4096)
      if not chunk:
        break
      response += chunk

    #response=response.decode("utf-8", errors="replace")

    status_code , headers, body = parse_response(response)
    unchunked_body = decode_chunked(body)
    print(f"Raw response: {response}")
    print()
    print(f"Status code: {status_code}")
    print()
    print(f"Chunked Body: {body}")
    print()
    print(f"Unchunked body: {unchunked_body}")

    s.close()

get_html("example.com")