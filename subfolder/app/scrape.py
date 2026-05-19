from bs4 import BeautifulSoup
import requests
import csv

url = "https://www.gutenberg.org/ebooks/bookshelf/671"
page = f"{url}?start_index="

response = requests.get(url)
print(response.status_code)

soup = BeautifulSoup(response.text, "html.parser")
books = []

for i in range(5):
    paginated_url = url if i == 0 else f"{page}{i * 25 + 1}"
    paginated_response = requests.get(paginated_url)
    paginated_soup = BeautifulSoup(paginated_response.text, "html.parser")
    start_index = i * 25 + 1
    end_index = start_index + 24
    page_index = f"{start_index}-{end_index}"

    for book in paginated_soup.find_all("li", class_="booklink"):
        books.append((page_index, book))

for index, book in books:
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

    print(f"Index: {index}, Title: {title}, by: {subtitle} with a total {download} downloads. For more: {link}")
    

with open("books.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Index", "Title", "Subtitle", "Downloads", "Link"])

    for index, book in books:
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

        writer.writerow([index, title, subtitle, download, link])