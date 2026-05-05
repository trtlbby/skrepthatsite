from bs4 import BeautifulSoup
import requests
import csv

url = "https://books.toscrape.com/"
response = requests.get(url)

print(response.status_code)

soup = BeautifulSoup(response.text, "html.parser")
books = soup.find_all("article", class_="product_pod")

for book in books:
    if book.h3 and book.h3.a:
        title = book.h3.a["title"]

    price = book.find("p", class_="price_color")
    if price:
        price_tag = price.text
    stock = book.find("p", class_="instock availability")
    if stock:
        stock_status = stock.text
        stock_stats = stock_status.strip()
    print(f"{title} - {price_tag} is {stock_stats}")

with open("books.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Price", "Stock Status"])

    for book in books:
        if book.h3 and book.h3.a:
            title = book.h3.a["title"]

        price = book.find("p", class_="price_color")
        if price:
            price_tag = price.text
        stock = book.find("p", class_="instock availability")
        if stock:
            stock_status = stock.text
            stock_stats = stock_status.strip()
        writer.writerow([title, price_tag, stock_stats])