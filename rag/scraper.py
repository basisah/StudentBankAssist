import requests
from bs4 import BeautifulSoup
import os,time

# List of URLs to scrape for RBC checkings, savings account, data from the government of Canada website on TFSA information
SCRAPE_URLS = [
    {"bank_name": "RBC", "account": "Checking", "url": "https://www.rbcroyalbank.com/bank-accounts/chequing-accounts/index.html"},
    {"bank_name": "RBC", "account": "day-to-day-checking", "url": "https://www.rbcroyalbank.com/bank-accounts/chequing-accounts/day-to-day-banking.html"},
    {"bank_name": "RBC", "account": "No-limit-banking", "url": "https://www.rbcroyalbank.com/bank-accounts/chequing-accounts/signature-no-limit-banking.html"},
    {"bank_name": "RBC", "account": "advantage-banking", "url": "https://www.rbcroyalbank.com/bank-accounts/chequing-accounts/advantage-banking.html"},
    {"bank_name": "RBC", "account": "vip-banking", "url": "https://www.rbcroyalbank.com/bank-accounts/chequing-accounts/vip-banking.html"},
    {"bank_name": "RBC", "account": "enhanced-savings", "url": "https://www.rbcroyalbank.com/bank-accounts/savings-accounts/enhanced-savings.html"},
    {"bank_name": "RBC", "account": "high-interest-savings", "url": "https://www.rbcroyalbank.com/bank-accounts/savings-accounts/high-interest-savings-account.html"},
    {"bank_name": "RBC", "account": "day-to-day-savings", "url": "https://www.rbcroyalbank.com/bank-accounts/savings-accounts/day-to-day-savings.html"},
    {"bank_name": "RBC", "account": "NOMI-find-and-safe", "url": "https://www.rbcroyalbank.com/bank-accounts/nomi-find-and-save.html"},
    {"bank_name": "RBC", "account": "TFSA", "url": "https://www.rbcdirectinvesting.com/accounts-investments/tfsa.html"},
    {"bank_name": "Government of Canada", "account": "TFSA", "url": "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account-tfsa.html"}
]
#Function to retrieve all sublinks from a given hub URL and filter them based on the base URL
def get_sublinks(hub_url:str, base_url:str): 
    """
    Get all sublinks from a given hub URL and filter them based on the base URL.

    Args:
        hub_url (str): The URL of the hub page to scrape for links.
        base_url (str): The base URL to filter the links.

    Returns:
        list: A list of filtered sublinks that start with the base URL.
    """
    r = requests.get(hub_url,headers={'User-Agent': 'Mozilla/5.0'},timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith(base_url):
            full = "https://www.canada.ca" + href 
            if full not in links and full !=hub_url:
                links.append(full)
    return links


# Function to scrape data from a RBC checkings, savings account, data from the government of Canada website on TFSA information
def scrape(url:str) -> str:
    """
    Scrape data from a given URL.
    Remove the nav, footer, and header sections to focus on the main content.

    Args:
        url (str): The URL to scrape data from.

    Returns:
        str: The scraped data as a string.
    """
    response = requests.get(url,headers={'User-Agent': 'Mozilla/5.0'},timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    for tag in soup(['nav', 'footer', 'header', 'script', 'style']):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)

# Function to just run the loop and complete the scraping
def scrape_all():
    os.makedirs("data/scraped", exist_ok=True)
    for source in SCRAPE_URLS:
        try:
            text = scrape(source["url"])
            with open(f"data/scraped/{source['account']}.txt", "w") as f:
                f.write(text)
            print(f"Scraped: {source['account']} from {source['bank_name']}")
        except Exception as e:
            print(f"Failed: {source['account']} — {e}")
        time.sleep(1)

    # Scrape TFSA sub-pages
    tfsa_links = get_sublinks(
        "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account.html",
        "/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account/"
    )
    for i, url in enumerate(tfsa_links):
        try:
            text = scrape(url)
            with open(f"data/scraped/canada_tfsa_{i}.txt", "w") as f:
                f.write(text)
            print(f"Scraped: {url}")
        except Exception as e:
            print(f"Failed: {url} — {e}")
        time.sleep(1)

if __name__ == "__main__":
    scrape_all()
