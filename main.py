import argparse
import asyncio
from crawler import crawl

# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--domain', required=True, help='Domain to crawl')
parser.add_argument('--rate', type=int, default=20, help='Number of concurrent requests')
args = parser.parse_args()

# Set the domain to crawl
domain = args.domain

# Set the initial URL to crawl
url = 'https://' + domain

# Start crawling all sublinks in the queue
asyncio.run(crawl(url, domain, args.rate))

