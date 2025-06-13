import requests
from bs4 import BeautifulSoup
import csv
import re
from urllib.parse import urljoin

url = "https://portland.craigslist.org/search/sya?query=laptop"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(url, headers=headers)
if response.status_code != 200:
    raise Exception(f"Failed to fetch page with status {response.status_code}")

soup = BeautifulSoup(response.text, "html.parser")
ads = soup.select("li.cl-static-search-result")

with open("laptops_detailed.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = [
        "title", "price", "location", "url", "posted_date",
        "image_url", "condition", "description", "post_id", "seller_type"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for ad in ads:
        # Basic info from search page
        title_elem = ad.select_one("div.title")
        price_elem = ad.select_one("div.price")
        location_elem = ad.select_one("div.location")
        link_elem = ad.select_one("a")
        date_elem = ad.find("div", class_=re.compile(r"posted-date"))
        img_elem = ad.select_one("img")

        title = title_elem.text.strip() if title_elem else ""
        price = price_elem.text.strip() if price_elem else ""
        location = location_elem.text.strip() if location_elem else ""
        ad_url = urljoin(url, link_elem["href"]) if link_elem else ""
        posted_date = date_elem.text.strip() if date_elem else ""
        image_url = img_elem["src"] if img_elem else ""

        # Fetch ad page for more details
        condition = ""
        description = ""
        post_id = ""
        seller_type = ""
        if ad_url:
            ad_response = requests.get(ad_url, headers=headers)
            if ad_response.status_code == 200:
                ad_soup = BeautifulSoup(ad_response.text, "html.parser")
                
                # Description
                desc_elem = ad_soup.select_one("#postingbody")
                description = desc_elem.text.strip() if desc_elem else ""
                
                # Condition
                cond_elem = ad_soup.find("p", class_="attrgroup")
                if cond_elem:
                    cond_span = cond_elem.find("span", string=re.compile(r"condition:", re.I))
                    condition = cond_span.text.replace("condition:", "").strip() if cond_span else ""
                
                # Post ID
                pid_elem = ad_soup.find("div", class_="postinginfos")
                if pid_elem:
                    pid_text = pid_elem.find("p", string=re.compile(r"post id:", re.I))
                    post_id = pid_text.text.replace("post id:", "").strip() if pid_text else ""
                
                # Seller type (owner/dealer)
                seller_elem = ad_soup.find("p", class_="attrgroup")
                if seller_elem:
                    seller_span = seller_elem.find("span", string=re.compile(r"for sale by:", re.I))
                    seller_type = seller_span.text.replace("for sale by:", "").strip() if seller_span else ""

        writer.writerow({
            "title": title,
            "price": price,
            "location": location,
            "url": ad_url,
            "posted_date": posted_date,
            "image_url": image_url,
            "condition": condition,
            "description": description,
            "post_id": post_id,
            "seller_type": seller_type
        })

print("Results saved to laptops_detailed.csv")