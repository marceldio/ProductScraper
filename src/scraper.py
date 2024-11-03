import requests
from bs4 import BeautifulSoup

class ProductScraper:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_html(self):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()  # Проверка на успешный статус запроса
            return response.text
        except requests.RequestException as e:
            print(f"Ошибка при получении HTML: {e}")
            return None

if __name__ == "__main__":
    url = "https://goldapple.ru/parfjumerija"
    scraper = ProductScraper(url)

    html_content = scraper.fetch_html()
    if html_content:
        print("HTML успешно получен!")
    else:
        print("Не удалось получить HTML.")
