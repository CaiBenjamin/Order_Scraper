"""
Tests for Costco email parser.
Essential tests to verify core scraper functionality.
"""

import pytest
from scraper.imap_scraper import parse_costco_email
from tests.fixtures.costco_emails import TEST_CASES


class TestCostcoEmailParser:
    """Core tests for Costco order scraper."""
    
    def test_extract_confirmed_order(self):
        """Can it extract Order Confirmed correctly?"""
        subject = "Your Costco.com Order Number 1261457232 is Confirmed"
        body = """
        <html><body>
            <img alt="AirPods 4 with Active Noise Cancellation" />
            <div>Order Number: 1261457232</div>
            <div>Status: Confirmed</div>
        </body></html>
        """
        
        result = parse_costco_email(subject, body)
        
        assert result is not None, "Should parse confirmed order"
        assert result["order_number"] == "1261457232", "Should extract order number"
        assert result["status"] == "Confirmed", "Should detect confirmed status"
        assert "AirPods" in result["product_name"], "Should extract product name"
    
    def test_extract_shipped_order(self):
        """Can it extract Order Shipped correctly?"""
        subject = "Your Costco.com Order Number 1261326992 Was Shipped"
        body = """
        <html><body>
            <img alt="iPad, 128GB Wi-Fi (A16 chip), Silver" />
            <div>Order Number: 1261326992</div>
            <div>Status: Shipped</div>
            <div>Tracking Number: 1Z999AA10123456784</div>
        </body></html>
        """
        
        result = parse_costco_email(subject, body)
        
        assert result is not None, "Should parse shipped order"
        assert result["order_number"] == "1261326992", "Should extract order number"
        assert result["status"] == "Shipped", "Should detect shipped status"
        assert "iPad" in result["product_name"], "Should extract product name"
        assert result["tracking_number"] == "1Z999AA10123456784", "Should extract tracking number"
    
    def test_extract_cancelled_order(self):
        """Can it extract Order Cancelled correctly?"""
        subject = "Your Costco.com Order #1261580310 Was Cancelled"
        body = """
        <html><body>
            <img alt="Apple Watch Series 9 GPS 45mm" />
            <div>Order Number: 1261580310</div>
            <div>Status: Cancelled</div>
        </body></html>
        """
        
        result = parse_costco_email(subject, body)
        
        assert result is not None, "Should parse cancelled order"
        assert result["order_number"] == "1261580310", "Should extract order number"
        assert result["status"] == "Cancelled", "Should detect cancelled status"
        assert "Apple Watch" in result["product_name"], "Should extract product name"
    
    def test_extract_delivered_order(self):
        """Can it extract Order Delivered correctly?"""
        subject = "Your Costco.com Order Number 1260332022 Has Been Delivered"
        body = """
        <html><body>
            <img alt="MacBook Pro 14-inch M3 Pro chip, 512GB" />
            <div>Order Number: 1260332022</div>
            <div>Status: Delivered</div>
            <div>Tracking Number: 1Z999AA10987654321</div>
        </body></html>
        """
        
        result = parse_costco_email(subject, body)
        
        assert result is not None, "Should parse delivered order"
        assert result["order_number"] == "1260332022", "Should extract order number"
        assert result["status"] == "Delivered", "Should detect delivered status"
        assert "MacBook" in result["product_name"], "Should extract product name"
        assert result["tracking_number"] == "1Z999AA10987654321", "Should extract tracking number"
    
    def test_find_product_name_from_alt_attribute(self):
        """Can it find the actual product name?"""
        subject = "Your Costco.com Order Number 1234567890 is Confirmed"
        body = """
        <html><body>
            <img alt="iPhone 15 Pro Max 256GB - Natural Titanium" />
            <div>Order details</div>
        </body></html>
        """
        
        result = parse_costco_email(subject, body)
        
        assert result is not None, "Should parse email"
        assert "iPhone" in result["product_name"], "Should extract product from alt attribute"
        assert result["product_name"] != "Unknown Product", "Should not return unknown product"
    
    def test_find_product_name_from_html_div(self):
        """Can it find product name when not in alt attribute?"""
        subject = "Your Costco.com Order Number 1260518616 is Confirmed"
        body = """
        <html><body>
            <div class="P88qxe">AirPods Pro 2nd Generation</div>
            <div>1 item from Costco</div>
        </body></html>
        """
        
        result = parse_costco_email(subject, body)
        
        assert result is not None, "Should parse email"
        assert "AirPods Pro" in result["product_name"], "Should extract product from div"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
