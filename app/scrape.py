from bs4 import BeautifulSoup
import requests
import csv

url = "https://www.gutenberg.org/ebooks/bookshelf/671"

response = requests.get(url)
print(response.status_code)

soup = BeautifulSoup(response.text, "html.parser")
books = soup.find_all("li", class_="booklink")

for book in books:
    title_tag = book.find("span", class_="title")
    subtitle_tag = book.find("span", class_="subtitle")
    download_tag = book.find("span", class_="extra")
    link_tag = book.find("a", class_="link")

    if not (title_tag and subtitle_tag and download_tag and link_tag):
        continue

    title = title_tag.get_text(strip=True)
    subtitle = subtitle_tag.get_text(strip=True)
    download = download_tag.get_text(strip=True)
    link = link_tag.get("href", "")

    print(f"Title: {title}, by: {subtitle} with a total {download} downloads. For more: {link}")
    

with open("books.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Title", "Subtitle", "Downloads", "Link"])

    for book in books:
        title_tag = book.find("span", class_="title")
        subtitle_tag = book.find("span", class_="subtitle")
        download_tag = book.find("span", class_="extra")
        link_tag = book.find("a", class_="link")

        if not (title_tag and subtitle_tag and download_tag and link_tag):
            continue

        title = title_tag.get_text(strip=True)
        subtitle = subtitle_tag.get_text(strip=True)
        download = download_tag.get_text(strip=True)
        link = link_tag.get("href", "")

        writer.writerow([title, subtitle, download, link])