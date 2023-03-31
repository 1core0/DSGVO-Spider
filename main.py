import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import argparse
from tqdm import tqdm

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--domain', required=True, help='Domain to crawl')
args = parser.parse_args()

# Set the domain to crawl
domain = args.domain

# Set the initial URL to crawl
url = 'https://' + domain
visited_urls = set()

# Create a queue to store sublinks
sublinks_queue = [url]

# Recursive function to crawl all links
async def crawl(url):
    visited_urls.add(url)
    print("Crawling: ", url)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                content = await response.read()
        except asyncio.TimeoutError:
            print(f"Timed out while requesting: {url}")
            return

    soup = BeautifulSoup(content, 'html.parser')
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href is None:
            continue

        # Construct the absolute URL of the link
        abs_url = urljoin(url, href)
        parsed_url = urlparse(abs_url)

        # Follow links to subdomains and other domains
        if parsed_url.netloc.endswith(domain) and abs_url not in visited_urls and abs_url not in sublinks_queue:
            sublinks_queue.append(abs_url)
            print("Found sublink: ", abs_url)

    # Recursively crawl sublinks
    tasks = []
    for sublink in sublinks_queue:
        if sublink not in visited_urls:
            task = asyncio.create_task(crawl(sublink))
            tasks.append(task)
    await asyncio.gather(*tasks)

# Start crawling all sublinks in the queue
asyncio.run(crawl(url))

