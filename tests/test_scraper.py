# tests/test_scraper.py
import pytest
from rag.scraper import scrape, get_sublinks, SCRAPE_URLS


def test_scrape_returns_text():
    """scrape() should return a non-empty string of readable text"""
    text = scrape("https://www.rbcroyalbank.com/bank-accounts/chequing-accounts/day-to-day-banking.html")
    assert isinstance(text, str)
    assert len(text) > 100  # should have substantial content


def test_scrape_removes_html_tags():
    """scraped text should not contain HTML tags"""
    text = scrape("https://www.rbcroyalbank.com/bank-accounts/chequing-accounts/day-to-day-banking.html")
    assert "<nav>" not in text
    assert "<script>" not in text
    assert "<header>" not in text


def test_scrape_handles_bad_url():
    """scrape() should raise an exception for invalid URLs"""
    with pytest.raises(Exception):
        scrape("https://www.rbcroyalbank.com/this-page-does-not-exist-12345")


def test_scrape_urls_list_not_empty():
    """SCRAPE_URLS should have entries to scrape"""
    assert len(SCRAPE_URLS) > 0


def test_scrape_urls_have_required_keys():
    """Every entry in SCRAPE_URLS should have account and url keys"""
    for source in SCRAPE_URLS:
        assert "account" in source, f"Missing 'account' key in {source}"
        assert "url" in source, f"Missing 'url' key in {source}"
        assert source["url"].startswith("http"), f"Invalid URL: {source['url']}"


def test_get_sublinks_returns_list():
    """get_sublinks() should return a list of URLs"""
    links = get_sublinks(
        "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account.html",
        "/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account/"
    )
    assert isinstance(links, list)
    assert len(links) > 0


def test_get_sublinks_returns_valid_urls():
    """Every link returned should be a full canada.ca URL"""
    links = get_sublinks(
        "https://www.canada.ca/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account.html",
        "/en/revenue-agency/services/tax/individuals/topics/tax-free-savings-account/"
    )
    for link in links:
        assert link.startswith("https://www.canada.ca"), f"Bad URL: {link}"