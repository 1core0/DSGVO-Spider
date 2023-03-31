import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from tqdm import tqdm
import asyncio

# Set up global variables
visited_urls = set()
sublinks_queue = set()

async def crawl(url, domain, async_limit):
    # Add the URL to the set of visited URLs
    visited_urls.add(url)
    print("Crawling: ", url)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=50) as response:
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
            sublinks_queue.add(abs_url)
            print("Found sublink: ", abs_url)

    # Recursively crawl sublinks with Semaphore
    tasks = []
    async with asyncio.Semaphore(async_limit):
        for sublink in sublinks_queue:
            if sublink not in visited_urls:
                task = asyncio.create_task(crawl(sublink, domain, async_limit))
                tasks.append(task)
    sublinks_queue.clear()
    for coro in asyncio.as_completed(tasks):
        await coro

