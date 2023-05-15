"""Tests for product data models."""

from capterra_scraper.models.product import Product, CategoryInfo


class TestProduct:
    def test_from_ssr_data_basic(self):
        raw = {
            "category": {"htmlName": "/accounting-software", "id": 42, "longName": "Accounting"},
            "vendor": {"url": "https://example.com", "name": "TestCo", "yearFounded": 2010, "location": "US"},
            "productUrl": "/p/test-product/",
            "productId": 123,
            "name": "TestProduct",
            "overallRating": 4.5,
            "reviewsTotal": 200,
            "shortDescription": "Short desc",
            "longDescription": "Long desc",
            "valueForMoneyRating": 4.0,
            "customerServiceRating": 4.2,
            "easeOfUseRating": 4.3,
            "recommendationRating": 4.1,
            "functionalityRating": 4.4,
            "pricingDetails": "From $10/mo",
            "pricing": "$10",
            "hasFreeTrial": True,
            "training": [{"name": "Webinars"}, {"name": "Docs"}],
            "support": [{"name": "Email"}, {"name": "Phone"}],
            "bestFor": "Small businesses",
        }

        product = Product.from_ssr_data(raw)

        assert product.name == "TestProduct"
        assert product.product_id == 123
        assert product.rating == 4.5
        assert product.review_count == 200
        assert product.capterra_url == "https://www.capterra.com/p/test-product/"
        assert product.category_url == "https://www.capterra.com/accounting-software"
        assert product.has_free_trial is True
        assert product.training == ["Webinars", "Docs"]
        assert product.support == ["Email", "Phone"]

    def test_from_ssr_data_missing_optional_fields(self):
        raw = {
            "category": {"htmlName": "software", "id": 1, "longName": "Software"},
            "vendor": {"url": "", "name": "", "yearFounded": None, "location": ""},
            "productUrl": "p/minimal",
            "productId": 1,
            "name": "Minimal",
            "overallRating": None,
            "reviewsTotal": 0,
            "shortDescription": "",
            "longDescription": "",
            "valueForMoneyRating": None,
            "customerServiceRating": None,
            "easeOfUseRating": None,
            "recommendationRating": None,
            "functionalityRating": None,
            "pricingDetails": "",
            "pricing": "",
            "hasFreeTrial": False,
            "training": [],
            "support": [],
            "bestFor": "",
        }

        product = Product.from_ssr_data(raw)
        assert product.name == "Minimal"
        assert product.rating is None

    def test_to_dict_returns_all_fields(self):
        product = Product(name="Test", product_id=1)
        d = product.to_dict()
        assert d["name"] == "Test"
        assert "category_url" in d
        assert "training" in d

