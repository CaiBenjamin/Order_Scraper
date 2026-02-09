"""
Test fixtures containing sample Costco email subjects and bodies.
These are realistic examples based on actual Costco order emails.
"""

# Confirmed Order Email
CONFIRMED_SUBJECT = "Your Costco.com Order Number 1261457232 is Confirmed"
CONFIRMED_BODY = """
<html>
<body>
<div>
  <img src="logo.png" alt="Costco Wholesale" />
  <h1>Order Confirmed</h1>
  <div class="order-details">
    <div class="product">
      <img src="product.jpg" alt="AirPods 4 with Active Noise Cancellation" />
      <div class="P88qxe">AirPods 4 with Active Noise Cancellation</div>
      <div>1 item from Costco</div>
    </div>
    <div>Order Number: 1261457232</div>
    <div>Status: Confirmed</div>
  </div>
</div>
</body>
</html>
"""

# Shipped Order Email
SHIPPED_SUBJECT = "Your Costco.com Order Number 1261326992 Was Shipped"
SHIPPED_BODY = """
<html>
<body>
<div>
  <img src="logo.png" alt="Costco Wholesale" />
  <h1>Order Shipped</h1>
  <div class="order-details">
    <div class="product">
      <img src="product.jpg" alt="iPad, 128GB Wi-Fi (A16 chip), Silver" />
      <div class="P88qxe">iPad, 128GB Wi-Fi (A16 chip), Silver</div>
      <div>1 item from Costco</div>
    </div>
    <div>Order Number: 1261326992</div>
    <div>Status: Shipped</div>
    <div>Tracking Number: 1Z999AA10123456784</div>
    <div>Track your package: <a href="https://www.ups.com/track?tracknum=1Z999AA10123456784">UPS Tracking</a></div>
  </div>
</div>
</body>
</html>
"""

# Cancelled Order Email
CANCELLED_SUBJECT = "Your Costco.com Order #1261580310 Was Cancelled"
CANCELLED_BODY = """
<html>
<body>
<div>
  <img src="logo.png" alt="Costco Wholesale" />
  <h1>Order Cancelled</h1>
  <div class="order-details">
    <div class="product">
      <img src="product.jpg" alt="Apple Watch Series 9 GPS 45mm" />
      <div class="P88qxe">Apple Watch Series 9 GPS 45mm</div>
      <div>1 item from Costco</div>
    </div>
    <div>Order Number: 1261580310</div>
    <div>Status: Cancelled</div>
    <div>Your order has been cancelled and you will not be charged.</div>
  </div>
</div>
</body>
</html>
"""

# Delivered Order Email
DELIVERED_SUBJECT = "Your Costco.com Order Number 1260332022 Has Been Delivered"
DELIVERED_BODY = """
<html>
<body>
<div>
  <img src="logo.png" alt="Costco Wholesale" />
  <h1>Order Delivered</h1>
  <div class="order-details">
    <div class="product">
      <img src="product.jpg" alt="MacBook Pro 14-inch M3 Pro chip, 512GB" />
      <div class="P88qxe">MacBook Pro 14-inch M3 Pro chip, 512GB</div>
      <div>1 item from Costco</div>
    </div>
    <div>Order Number: 1260332022</div>
    <div>Status: Delivered</div>
    <div>Tracking Number: 1Z999AA10987654321</div>
    <div>Delivered on: January 28, 2026</div>
  </div>
</div>
</body>
</html>
"""

# Edge case: Product name in different location (no alt attribute)
NO_ALT_SUBJECT = "Your Costco.com Order Number 1260518616 is Confirmed"
NO_ALT_BODY = """
<html>
<body>
<div>
  <img src="logo.png" alt="Costco Wholesale" />
  <div class="order-details">
    <div class="product">
      <div class="P88qxe">iPhone 15 Pro Max 256GB - Natural Titanium</div>
      <div>1 item from Costco</div>
    </div>
    <div>Order Number: 1260518616</div>
  </div>
</div>
</body>
</html>
"""

# Edge case: Multiple products in one order (should extract first product)
MULTI_PRODUCT_SUBJECT = "Your Costco.com Order Number 1262000001 is Confirmed"
MULTI_PRODUCT_BODY = """
<html>
<body>
<div>
  <img src="logo.png" alt="Costco Wholesale" />
  <div class="order-details">
    <div class="product">
      <img src="p1.jpg" alt="AirPods Pro 2nd Generation" />
      <div>AirPods Pro 2nd Generation</div>
    </div>
    <div class="product">
      <img src="p2.jpg" alt="Apple Magic Keyboard" />
      <div>Apple Magic Keyboard</div>
    </div>
    <div>2 items from Costco</div>
    <div>Order Number: 1262000001</div>
  </div>
</div>
</body>
</html>
"""

# All test cases
TEST_CASES = [
    {
        "name": "confirmed_order",
        "subject": CONFIRMED_SUBJECT,
        "body": CONFIRMED_BODY,
        "expected": {
            "order_number": "1261457232",
            "status": "Confirmed",
            "product_name": "AirPods 4 with Active Noise Cancellation",
            "tracking_number": None
        }
    },
    {
        "name": "shipped_order",
        "subject": SHIPPED_SUBJECT,
        "body": SHIPPED_BODY,
        "expected": {
            "order_number": "1261326992",
            "status": "Shipped",
            "product_name": "iPad, 128GB Wi-Fi (A16 chip), Silver",
            "tracking_number": "1Z999AA10123456784"
        }
    },
    {
        "name": "cancelled_order",
        "subject": CANCELLED_SUBJECT,
        "body": CANCELLED_BODY,
        "expected": {
            "order_number": "1261580310",
            "status": "Cancelled",
            "product_name": "Apple Watch Series 9 GPS 45mm",
            "tracking_number": None
        }
    },
    {
        "name": "delivered_order",
        "subject": DELIVERED_SUBJECT,
        "body": DELIVERED_BODY,
        "expected": {
            "order_number": "1260332022",
            "status": "Delivered",
            "product_name": "MacBook Pro 14-inch M3 Pro chip, 512GB",
            "tracking_number": "1Z999AA10987654321"
        }
    },
    {
        "name": "no_alt_attribute",
        "subject": NO_ALT_SUBJECT,
        "body": NO_ALT_BODY,
        "expected": {
            "order_number": "1260518616",
            "status": "Confirmed",
            "product_name": "iPhone 15 Pro Max 256GB - Natural Titanium",
            "tracking_number": None
        }
    },
    {
        "name": "multi_product_order",
        "subject": MULTI_PRODUCT_SUBJECT,
        "body": MULTI_PRODUCT_BODY,
        "expected": {
            "order_number": "1262000001",
            "status": "Confirmed",
            "product_name": "AirPods Pro 2nd Generation",
            "tracking_number": None
        }
    }
]
