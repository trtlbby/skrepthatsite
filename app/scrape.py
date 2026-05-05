from bs4 import BeautifulSoup
import requests

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
        ok = book.find("i", class_="icon-ok")
        stock_status = stock.text
    print(f"{title} - {price_tag} is {stock_status}")
