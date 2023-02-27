import requests
import sqlite3
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# Connect to SQLite database
conn = sqlite3.connect('sqllite.db')
c = conn.cursor()

# Create cookies table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS cookies
             (url TEXT, name TEXT, value TEXT)''')

# Set the domain to crawl
domain = 'example.com'

# Set the cookie policy
cookie_policy = 'selective'  # Options: 'accept', 'decline', 'selective'

# Set the initial URL to crawl
url = 'https://' + domain
visited_urls = set()

# Recursive function to crawl all links
def crawl(url):
    if url in visited_urls:
        return
    visited_urls.add(url)
    
    # Send a GET request to the URL and get the HTML content
    try:
        response = requests.get(url, timeout=5)
    except requests.exceptions.Timeout:
        print("Request timed out for URL:", url)
        return
    except requests.exceptions.ConnectionError:
        print("Failed to connect to URL:", url)
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract all links from the HTML content
    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if href is None:
            continue
        
        # Construct the absolute URL of the link
        abs_url = urljoin(url, href)
        parsed_url = urlparse(abs_url)

        # Follow links to subdomains and other domains
        if parsed_url.netloc.endswith(domain):
            crawl(abs_url)
        else:
            print("Following link to external domain:", abs_url)
            try:
                response = requests.get(abs_url, timeout=5)
                print("Visited external URL:", abs_url)
            except requests.exceptions.Timeout:
                print("Request timed out for URL:", abs_url)
            except requests.exceptions.ConnectionError:
                print("Failed to connect to URL:", abs_url)
            continue
        
        # Store cookies in the database
        cookies = response.cookies
        for cookie in cookies:
            cookie_name = cookie.name
            cookie_value = cookie.value
            
            if cookie_policy == 'accept':
                c.execute('INSERT INTO cookies (url, name, value) VALUES (?, ?, ?)', (abs_url, cookie_name, cookie_value))
            elif cookie_policy == 'decline':
                continue
            elif cookie_policy == 'selective':
                print('Do you want to accept the following cookie?')
                print('URL:', abs_url)
                print('Name:', cookie_name)
                print('Value:', cookie_value)
                choice = input('Enter "y" to accept or "n" to decline: ')
                if choice == 'y':
                    c.execute('INSERT INTO cookies (url, name, value) VALUES (?, ?, ?)', (abs_url, cookie_name, cookie_value))
    
    conn.commit()

# Start crawling the initial URL
crawl(url)

# Close the database connection
conn.close()
