import requests
import json

class ProductScraper:
    def __init__(self, base_url, api_url, timeout=60):
        self.base_url = base_url
        self.api_url = api_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
        }
        self.timeout = timeout

    def fetch_data(self):
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при получении данных: {e}")
            return None

    def fetch_product_details(self, product_id):
        """Получение детальной информации о товаре."""
        try:
            # Новый URL для получения данных о продукте
            product_url = f"{self.base_url}/front/api/catalog/product-card/base?itemId={product_id}&cityId=0c5b2444-70a0-4932-980c-b4dc0d3f02b5&customerGroupId=0&z=14-46"
            print(f"Запрос к URL продукта: {product_url}")
            response = requests.get(product_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            product_data = response.json().get("data", {})

            # Извлечение информации с учетом новой структуры
            description = product_data.get("productDescription", [])[0].get("content", "Нет описания") if len(product_data.get("productDescription", [])) > 0 else "Нет описания"
            usage_instructions = product_data.get("productDescription", [])[1].get("content", "Нет инструкции") if len(product_data.get("productDescription", [])) > 1 else "Нет инструкции"
            country = product_data.get("productDescription", [])[3].get("subtitle", "Не указана") if len(product_data.get("productDescription", [])) > 3 else "Не указана"

            return {
                "description": description,
                "usage_instructions": usage_instructions,
                "country": country,
            }
        except requests.RequestException as e:
            print(f"Ошибка при получении данных о продукте: {e}")
            return {
                "description": "Нет описания",
                "usage_instructions": "Нет инструкции",
                "country": "Не указана",
            }

    def parse_products(self, data):
        products = []
        product_list = data.get("products") or data.get("data", {}).get("products")

        if not product_list:
            print("Не удалось найти список продуктов в JSON-ответе.")
            return products

        for item in product_list:
            try:
                link = f"{self.base_url}{item['url']}"
                name = item.get("name", "Нет названия")
                brand = item.get("brand", "Нет бренда")
                regular_price = item.get("price", {}).get("regular", {}).get("amount", "Нет данных")
                actual_price = item.get("price", {}).get("actual", {}).get("amount", "Нет данных")
                rating = item.get("reviews", {}).get("rating", "Нет рейтинга")
                review_count = item.get("reviews", {}).get("reviewsCount", "Нет отзывов")
                image_url = item["imageUrls"][0]["url"].replace("${screen}", "fullhd").replace("${format}", "jpg")

                # Получаем дополнительные данные о продукте через JSON
                details = self.fetch_product_details(item["itemId"])

                products.append({
                    "link": link,
                    "name": name,
                    "brand": brand,
                    "regular_price": regular_price,
                    "actual_price": actual_price,
                    "rating": rating,
                    "review_count": review_count,
                    "image_url": image_url,
                    "description": details["description"],
                    "usage_instructions": details["usage_instructions"],
                    "country": details["country"]
                })
            except KeyError as e:
                print(f"Ошибка при извлечении данных для продукта: {e}")

        return products

# Запуск
if __name__ == "__main__":
    base_url = "https://goldapple.ru"
    api_url = "https://goldapple.ru/front/api/catalog/products?categoryId=1000003783&cityId=0c5b2444-70a0-4932-980c-b4dc0d3f02b5&pageNumber=1&z=14-46"

    scraper = ProductScraper(base_url, api_url)
    data = scraper.fetch_data()
    if data is not None:
        products = scraper.parse_products(data)
        print(f"Найдено товаров: {len(products)}")
        print(json.dumps(products, indent=2, ensure_ascii=False))
    else:
        print("Не удалось получить данные.")
