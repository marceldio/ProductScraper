import csv
import json
import os
import random
import re
import time

import requests
from requests.exceptions import HTTPError, Timeout


class ProductScraper:
    def __init__(self, base_url, api_url, timeout=15, max_retries=3):
        self.base_url = base_url
        self.api_url = api_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agents = [
            "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:131.0) Gecko/20100101 Firefox/131.0"
        ]

    def get_headers(self):
        return {
            "User-Agent": random.choice(self.user_agents),
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": self.base_url,
        }

    def fetch_data(self, page_number):
        url = f"{self.api_url}&pageNumber={page_number}"
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(
                    url, headers=self.get_headers(), timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            except (HTTPError, Timeout):
                if attempt < self.max_retries:
                    time.sleep(random.uniform(10, 20) * attempt)
                else:
                    return None

    def fetch_product_details(self, product_id):
        product_url = f"{self.base_url}/front/api/catalog/product-card/base?itemId={product_id}&cityId=0c5b2444-70a0-4932-980c-b4dc0d3f02b5&customerGroupId=0&z=14-46"
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.get(
                    product_url, headers=self.get_headers(), timeout=self.timeout
                )
                response.raise_for_status()
                product_data = response.json().get("data", {})

                description = self.clean_text(
                    self.extract_text(product_data.get("productDescription", []), 0)
                )
                usage_instructions = self.clean_text(
                    self.extract_text(product_data.get("productDescription", []), 1)
                )
                country = self.clean_text(self.extract_country(product_data))

                return {
                    "description": description,
                    "usage_instructions": usage_instructions,
                    "country": country,
                }
            except (HTTPError, Timeout):
                if attempt < self.max_retries:
                    time.sleep(random.uniform(10, 20) * attempt)
                else:
                    return None

    def clean_text(self, text):
        text = re.sub(r"<.*?>", " ", text)  # Убираем HTML-теги
        return " ".join(text.split())  # Убираем лишние пробелы

    def extract_text(self, descriptions, index):
        if len(descriptions) > index:
            return descriptions[index].get("content", "Нет информации")
        return "Нет информации"

    def extract_country(self, product_data):
        descriptions = product_data.get("productDescription", [])
        if len(descriptions) > 3:
            return descriptions[3].get("subtitle", "Не указана")
        return "Не указана"

    def parse_products(self):
        products = []
        page_number = 1

        while True:
            data = self.fetch_data(page_number)
            if not data:
                break
            product_list = data.get("products") or data.get("data", {}).get("products")

            if not product_list:
                break

            for item in product_list:
                try:
                    link = f"{self.base_url}{item['url']}"
                    name = item.get("name", "Нет названия")
                    brand = item.get("brand", "Нет бренда")
                    regular_price = item["price"]["regular"]["amount"]
                    actual_price = item["price"]["actual"]["amount"]

                    reviews_data = item.get("reviews", {})
                    rating = reviews_data.get("rating", "Нет рейтинга")
                    review_count = reviews_data.get("reviewsCount", "Нет отзывов")

                    details = self.fetch_product_details(item["itemId"])

                    products.append(
                        {
                            "link": link,
                            "name": name,
                            "brand": brand,
                            "regular_price": regular_price,
                            "actual_price": actual_price,
                            "rating": rating,
                            "review_count": review_count,
                            "description": (
                                details["description"] if details else "Нет описания"
                            ),
                            "usage_instructions": (
                                details["usage_instructions"]
                                if details
                                else "Нет инструкции"
                            ),
                            "country": details["country"] if details else "Не указана",
                        }
                    )
                except KeyError:
                    pass
            page_number += 1
        return products

    def save_to_csv(self, products, filename="output/products.csv"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=products[0].keys())
            writer.writeheader()
            writer.writerows(products)


if __name__ == "__main__":
    base_url = "https://goldapple.ru"
    api_url = "https://goldapple.ru/front/api/catalog/products?categoryId=1000003783&cityId=0c5b2444-70a0-4932-980c-b4dc0d3f02b5&z=14-46"

    scraper = ProductScraper(base_url, api_url)
    products = scraper.parse_products()  # Сбор всех товаров без ограничения
    print(f"Найдено товаров: {len(products)}")

    if products:
        scraper.save_to_csv(products)
        print(f"Данные сохранены в файл: output/products.csv")
