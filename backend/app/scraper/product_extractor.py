import re
from html import unescape
from urllib.parse import urljoin


def parse_price(text):
    m = re.search(r"\d[\d,]*(?:\.\d+)?", text)
    if not m:
        return None
    return float(m.group().replace(",", ""))


def extract_title(html):
    m = re.search(r"<h1>(.*?)</h1>", html, re.DOTALL)
    return unescape(m.group(1)).strip() if m else None


def extract_price(html):
    m = re.search(r'<p class="price_color">(.*?)</p>', html, re.DOTALL)
    if not m:
        return None
    return parse_price(unescape(m.group(1)))


def extract_image(html, page_url):
    m = re.search(r'<img src="([^"]+)"', html)
    return urljoin(page_url, m.group(1)) if m else None


def extract_product(html, page_url):
    return {
        "name": extract_title(html),
        "price": extract_price(html),
        "image": extract_image(html, page_url),
        "url": page_url,
    }


if __name__ == "__main__":
    from app.crawler.socket_client import fetch_url

    url = "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    status, headers, body, final_url = fetch_url(url)
    html = body.decode("utf-8", errors="replace")
    print(extract_product(html, final_url))