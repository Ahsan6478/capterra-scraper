"""Tests for data exporters."""

import json
import os
import tempfile

from capterra_scraper.models.product import Product
from capterra_scraper.exporters.csv_exporter import export_products_csv
from capterra_scraper.exporters.json_exporter import export_products_json, merge_json_files


class TestCsvExporter:
    def test_export_creates_file(self, tmp_path):
        products = [Product(name="A", product_id=1), Product(name="B", product_id=2)]
        output = str(tmp_path / "test.csv")
        export_products_csv(products, output)
        assert os.path.exists(output)

    def test_export_empty_list(self, tmp_path):
        output = str(tmp_path / "empty.csv")
        export_products_csv([], output)
        assert not os.path.exists(output)


class TestJsonExporter:
    def test_export_creates_file(self, tmp_path):
        products = [Product(name="A", product_id=1)]
        output = str(tmp_path / "test.json")
        export_products_json(products, output)
        assert os.path.exists(output)
        with open(output) as fh:
            data = json.load(fh)
        assert len(data) == 1
        assert data[0]["name"] == "A"


class TestMergeJsonFiles:
    def test_merge_deduplicates(self, tmp_path):
        # Create two JSON files with overlapping records
        file1 = [{"product_id": 1, "category_name": "A", "capterra_url": "/p/1"}]
        file2 = [
            {"product_id": 1, "category_name": "A", "capterra_url": "/p/1"},
            {"product_id": 2, "category_name": "B", "capterra_url": "/p/2"},
        ]
        with open(tmp_path / "f1.json", "w") as fh:
            json.dump(file1, fh)
        with open(tmp_path / "f2.json", "w") as fh:
            json.dump(file2, fh)

        output = str(tmp_path / "merged.json")
        count = merge_json_files(str(tmp_path), output)
        assert count == 2

    def test_fixes_double_slash_urls(self, tmp_path):
        records = [{"product_id": 1, "category_name": "A", "capterra_url": "https://www.capterra.com//p/123"}]
        with open(tmp_path / "data.json", "w") as fh:
            json.dump(records, fh)

        output = str(tmp_path / "fixed.json")
        merge_json_files(str(tmp_path), output)

        with open(output) as fh:
            data = json.load(fh)
        assert "//p" not in data[0]["capterra_url"]
