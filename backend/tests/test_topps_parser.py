"""
Tests for Topps email parser.
Essential tests to verify Topps scraper functionality.
"""

import pytest
from scraper.imap_scraper import parse_topps_email


class TestToppsEmailParser:
    """Core tests for Topps order scraper."""
    
    def test_extract_confirmed_order(self):
        """Can it extract Topps Order Confirmed correctly?"""
        subject = "Order US-12857405-S confirmed"
        body = """
        <html><body>
            <div>Product: 2024 Topps Chrome Baseball Hobby Box</div>
            <div>Order Number: US-12857405-S</div>
            <div>Status: Confirmed</div>
        </body></html>
        """
        
        result = parse_topps_email(subject, body)
        
        assert result is not None, "Should parse confirmed order"
        assert result["order_number"] == "US-12857405-S", "Should extract order number"
        assert result["status"] == "Confirmed", "Should detect confirmed status"
        assert "Topps" in result["product_name"], "Should have Topps in product name"
    
    def test_extract_canceled_order(self):
        """Can it extract Topps Order Canceled correctly?"""
        subject = "Order US-12857405-S has been canceled"
        body = """
        <html><body>
            <div>Product: 2024 Bowman Chrome Baseball</div>
            <div>Order Number: US-12857405-S</div>
            <div>Status: Canceled</div>
        </body></html>
        """
        
        result = parse_topps_email(subject, body)
        
        assert result is not None, "Should parse canceled order"
        assert result["order_number"] == "US-12857405-S", "Should extract order number"
        assert result["status"] == "Cancelled", "Should detect cancelled status"
    
    def test_extract_shipped_order(self):
        """Can it extract Topps Order Shipped correctly?"""
        subject = "Order US-12345678-S has shipped"
        body = """
        <html><body>
            <div>Product: 2024 Topps Series 1 Baseball</div>
            <div>Order Number: US-12345678-S</div>
            <div>Status: Shipped</div>
        </body></html>
        """
        
        result = parse_topps_email(subject, body)
        
        assert result is not None, "Should parse shipped order"
        assert result["order_number"] == "US-12345678-S", "Should extract order number"
        assert result["status"] == "Shipped", "Should detect shipped status"
    
    def test_order_number_format(self):
        """Can it handle the US-XXXXXXXX-S order format?"""
        subject = "Order US-99999999-S confirmed"
        body = "<html><body>Topps order details</body></html>"
        
        result = parse_topps_email(subject, body)
        
        assert result is not None, "Should parse email"
        assert result["order_number"] == "US-99999999-S", "Should extract correctly formatted order number"
        assert result["order_number"].startswith("US-"), "Order number should start with US-"
        assert result["order_number"].endswith("-S"), "Order number should end with -S"
    
    def test_non_topps_email_returns_none(self):
        """Should it ignore non-Topps emails?"""
        subject = "Welcome to Amazon Prime"
        body = "<html><body>Amazon content</body></html>"
        
        result = parse_topps_email(subject, body)
        
        assert result is None, "Non-Topps email should return None"
    
    def test_lowercase_order_number(self):
        """Can it extract lowercase order numbers and uppercase them?"""
        subject = "Order us-12345678-s confirmed"
        body = "<html><body>Your Topps order</body></html>"
        
        result = parse_topps_email(subject, body)
        
        assert result is not None, "Should parse email with lowercase order number"
        assert result["order_number"] == "US-12345678-S", "Should convert to uppercase"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
