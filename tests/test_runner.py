"""Tests for the runner module."""

from capterra_scraper.runner import _divide_list


class TestDivideList:
    def test_even_split(self):
        result = _divide_list([1, 2, 3, 4], 2)
        assert result == [[1, 2], [3, 4]]

    def test_uneven_split(self):
        result = _divide_list([1, 2, 3, 4, 5], 2)
        assert len(result) == 2
        assert len(result[0]) == 3
        assert len(result[1]) == 2

    def test_single_group(self):
        result = _divide_list([1, 2, 3], 1)
        assert result == [[1, 2, 3]]

    def test_empty_list(self):
        result = _divide_list([], 3)
        assert all(len(chunk) == 0 for chunk in result)

    def test_more_groups_than_items(self):
        result = _divide_list([1, 2], 5)
        non_empty = [c for c in result if c]
        assert len(non_empty) == 2

    def test_zero_groups(self):
        result = _divide_list([1, 2, 3], 0)
        assert result == [[1, 2, 3]]
