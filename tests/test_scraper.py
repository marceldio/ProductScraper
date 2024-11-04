import unittest
from unittest.mock import patch
from src.scraper import ProductScraper


class TestProductScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = ProductScraper(
            base_url="https://example.com",
            api_url="https://example.com/api",
            timeout=5,
            max_retries=3,
        )

    def test_clean_text(self):
        # Тест для метода clean_text
        text = "<p>Пример текста<br>с тегами</p>\nи переносами"
        cleaned = self.scraper.clean_text(text)
        self.assertEqual(cleaned, "Пример текста с тегами и переносами")

    @patch("src.scraper.requests.get")
    def test_fetch_data(self, mock_get):
        # Имитация успешного ответа для fetch_data
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": {"products": [{"id": 1}, {"id": 2}]}
        }

        data = self.scraper.fetch_data(page_number=1)
        self.assertIsNotNone(data)
        self.assertIn("products", data.get("data", {}))

    @patch("src.scraper.requests.get")
    def test_fetch_product_details(self, mock_get):
        # Имитация успешного ответа для fetch_product_details
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "data": {
                "productDescription": [
                    {"content": "Описание продукта"},
                    {"content": "Инструкция по применению"},
                    {},
                    {"subtitle": "Россия"},
                ]
            }
        }

        details = self.scraper.fetch_product_details(product_id="12345")
        self.assertIsNotNone(details)
        self.assertEqual(details["description"], "Описание продукта")
        self.assertEqual(details["usage_instructions"], "Инструкция по применению")
        self.assertEqual(details["country"], "Россия")

    @patch("src.scraper.ProductScraper.fetch_data")
    @patch("src.scraper.ProductScraper.fetch_product_details")
    def test_parse_products(self, mock_fetch_product_details, mock_fetch_data):
        # Имитация данных для parse_products
        mock_fetch_data.side_effect = [
            {
                "data": {
                    "products": [
                        {
                            "url": "/product/1",
                            "name": "Товар 1",
                            "brand": "Бренд 1",
                            "price": {
                                "regular": {"amount": 1000},
                                "actual": {"amount": 800},
                            },
                            "reviews": {"rating": 4.5, "reviewsCount": 10},
                            "imageUrls": [{"url": "image1.jpg"}],
                            "itemId": "12345",
                        }
                    ]
                }
            },
            None,  # Остановка после первой страницы
        ]
        mock_fetch_product_details.return_value = {
            "description": "Описание продукта",
            "usage_instructions": "Инструкция по применению",
            "country": "Россия",
        }

        products = self.scraper.parse_products(max_items=1)
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0]["name"], "Товар 1")
        self.assertEqual(products[0]["brand"], "Бренд 1")
        self.assertEqual(products[0]["regular_price"], 1000)
        self.assertEqual(products[0]["actual_price"], 800)
        self.assertEqual(products[0]["rating"], 4.5)
        self.assertEqual(products[0]["review_count"], 10)
        self.assertEqual(products[0]["description"], "Описание продукта")
        self.assertEqual(products[0]["usage_instructions"], "Инструкция по применению")
        self.assertEqual(products[0]["country"], "Россия")


if __name__ == "__main__":
    unittest.main()
