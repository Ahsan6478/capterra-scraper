"""Tests for the product spider's HTML parsing."""

from capterra_scraper.spiders.product_spider import _parse_ssr_bridge_data


class TestParseSSRBridgeData:
    def test_extracts_product_from_valid_html(self):
        ssr_data = (
            '{"category": {"htmlName": "/crm", "id": 1, "longName": "CRM"},'
            '"vendor": {"url": "https://test.com", "name": "V", "yearFounded": 2020, "location": "US"},'
            '"productUrl": "/p/test/", "productId": 99, "name": "CRM Tool",'
            '"overallRating": 4.0, "reviewsTotal": 50, "shortDescription": "sd",'
            '"longDescription": "ld", "valueForMoneyRating": 3.5,'
            '"customerServiceRating": 4.0, "easeOfUseRating": 4.1,'
            '"recommendationRating": 3.9, "functionalityRating": 4.2,'
            '"pricingDetails": "$5", "pricing": "$5/mo", "hasFreeTrial": true,'
            '"training": [{"name": "Live"}], "support": [{"name": "Chat"}],'
            '"bestFor": "SMBs", "rank": 1, "alternativeProducts": []}'
        )
        html = (
            "<html><head>"
            f"<script>window['SSR_BRIDGE_DATA'] = {ssr_data}</script>"
            "</head><body></body></html>"
        )
        product = _parse_ssr_bridge_data(html)
        assert product is not None
        assert product.name == "CRM Tool"
        assert product.product_id == 99

    def test_returns_none_for_missing_script(self):
        html = "<html><body>No script here</body></html>"
        result = _parse_ssr_bridge_data(html)
        assert result is None

    def test_returns_none_for_invalid_json(self):
        html = (
            "<html><script>window['SSR_BRIDGE_DATA'] = {invalid json rank alternativeProducts</script></html>"
        )
        result = _parse_ssr_bridge_data(html)
        assert result is None
