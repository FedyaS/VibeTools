import requests
from bs4 import BeautifulSoup
import csv
import re

url = "https://portland.craigslist.org/search/sya?query=laptop"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    raise Exception(f"Failed to fetch page with status {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")
ads = soup.select("li.cl-static-search-result")

with open("laptops.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["title", "price", "location", "url", "posted_date"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for ad in ads:
        title_elem = ad.select_one("div.title")
        price_elem = ad.select_one("div.price")
        location_elem = ad.select_one("div.location")
        link_elem = ad.select_one("a")
        date_elem = ad.find("div", class_=re.compile(r"posted-date"))

        title = title_elem.text.strip() if title_elem else ""
        price = price_elem.text.strip() if price_elem else ""
        location = location_elem.text.strip() if location_elem else ""
        url = link_elem["href"] if link_elem else ""
        posted_date = date_elem.text.strip() if date_elem else ""

        writer.writerow({
            "title": title,
            "price": price,
            "location": location,
            "url": url,
            "posted_date": posted_date
        })

print("Results saved to laptops.csv")