import socket
import ssl
import certifi
from urllib.parse import urlparse, urljoin
import re
from html import unescape

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

def extract_title(html):
    m = re.search(r'id="productTitle"[^>]*>(.*?)</span>', html, re.DOTALL)
    if not m:
        return None
    return unescape(m.group(1)).strip()


def get_html(host, path="/", port=443, use_tls=True):
    s = socket.socket()
    s.settimeout(10)
    s.connect((host, port))

    if use_tls:
        context = ssl.create_default_context(cafile=certifi.where())
        s = context.wrap_socket(s, server_hostname=host)

    # print(f"Connect to : {s.getpeername()}")
    request = (
    f"GET {path} HTTP/1.1\r\n"
    f"Host: {host}\r\n"
    f"Accept-Encoding: identity\r\n"
    f"Connection: close\r\n\r\n"
    )

    s.sendall(request.encode("utf-8"))

    response = b""
    while True:
      chunk = s.recv(4096)
      if not chunk:
        break
      response += chunk
    s.close()
    #response=response.decode("utf-8", errors="replace")

    status_code , headers, body = parse_response(response)
    if "chunked" in headers.get("transfer-encoding", "").lower():
        body = decode_chunked(body)

    return status_code, headers, body


def fetch_url(url, max_redirects=5):
    for _ in range(max_redirects + 1):
        parts = urlparse(url)
        use_tls = parts.scheme == "https"
        host = parts.hostname
        port = parts.port or (443 if use_tls else 80)
        path = parts.path or "/"
        if parts.query:
            path += "?" + parts.query

        status, headers, body = get_html(host, path, port, use_tls)

        if status in (301, 302, 303, 307, 308) and "location" in headers:
            url = urljoin(url, headers["location"])
            print("redirect ->", url)
            continue

        return status, headers, body, url

    raise RuntimeError("Too many redirects")

#test block
if __name__ == "__main__":
    url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    status, headers, body, final_url = fetch_url(url)
    html = body.decode("utf-8", errors="replace")

    for marker in ["<h1>", "price_color", "<img"]:
        i = html.find(marker)
        print(marker, "->", i)
        if i != -1:
            print(html[max(i - 40, 0):i + 200])
        print("-----")

    print(status, final_url)
    print("length:", len(html))
    print(html[:300])