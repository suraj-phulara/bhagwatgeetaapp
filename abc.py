import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import xml.etree.ElementTree as ET

def get_links(url, base_url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = set()

        for a_tag in soup.find_all('a', href=True):
            link = a_tag['href']
            full_link = urljoin(base_url, link)
            # Only include links that are within the same domain
            if urlparse(full_link).netloc == urlparse(base_url).netloc:
                links.add(full_link)
        return links
    except requests.RequestException as e:
        print(f"Failed to retrieve {url}: {e}")
        return set()

def crawl_website(base_url):
    to_crawl = set([base_url])
    crawled = set()
    all_links = set()

    while to_crawl:
        url = to_crawl.pop()
        if url not in crawled:
            print(f"Crawling: {url}")
            links = get_links(url, base_url)
            all_links.update(links)
            to_crawl.update(links - crawled)
            crawled.add(url)
            time.sleep(1)  # Be polite and don't overload the server

    return all_links

def generate_sitemap(urls, base_url):
    urlset = ET.Element('urlset', {
        'xmlns': "http://www.sitemaps.org/schemas/sitemap/0.9",
        'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
        'xsi:schemaLocation': "http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"
    })

    for url in urls:
        url_element = ET.SubElement(urlset, 'url')
        loc = ET.SubElement(url_element, 'loc')
        loc.text = url
        lastmod = ET.SubElement(url_element, 'lastmod')
        lastmod.text = time.strftime('%Y-%m-%dT%H:%M:%S+00:00')
        priority = ET.SubElement(url_element, 'priority')
        priority.text = "0.80" if url != base_url else "1.00"

    tree = ET.ElementTree(urlset)
    tree.write('sitemap.xml', encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    base_url = 'https://www.holy-bhagavad-gita.org'
    all_urls = crawl_website(base_url)

    generate_sitemap(all_urls, base_url)

    print(f'Extracted {len(all_urls)} URLs and generated sitemap.xml')
