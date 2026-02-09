"""
Test fixtures containing sample Topps email subjects and bodies.
"""

# Confirmed Order Email
CONFIRMED_SUBJECT = "Order US-12857405-S confirmed"
CONFIRMED_BODY = """
<html>
<body>
<div>
  <h1>Order Confirmed</h1>
  <p>Your order US-12857405-S has been confirmed.</p>
  <div>Product: 2024 Topps Chrome Baseball Hobby Box</div>
  <div>Order Number: US-12857405-S</div>
  <div>Status: Confirmed</div>
</div>
</body>
</html>
"""

# Canceled Order Email
CANCELED_SUBJECT = "Order US-12857405-S has been canceled"
CANCELED_BODY = """
<html>
<body>
<div>
  <h1>Order Canceled</h1>
  <p>Your order US-12857405-S has been canceled.</p>
  <div>Product: 2024 Bowman Chrome Baseball</div>
  <div>Order Number: US-12857405-S</div>
  <div>Status: Canceled</div>
</div>
</body>
</html>
"""

# Shipped Order Email (rare but possible)
SHIPPED_SUBJECT = "Order US-12345678-S has shipped"
SHIPPED_BODY = """
<html>
<body>
<div>
  <h1>Order Shipped</h1>
  <p>Your order US-12345678-S has shipped.</p>
  <div>Product: 2024 Topps Series 1 Baseball Blaster Box</div>
  <div>Order Number: US-12345678-S</div>
  <div>Status: Shipped</div>
</div>
</body>
</html>
"""

# All test cases
TOPPS_TEST_CASES = [
    {
        "name": "topps_confirmed_order",
        "subject": CONFIRMED_SUBJECT,
        "body": CONFIRMED_BODY,
        "expected": {
            "order_number": "US-12857405-S",
            "status": "Confirmed",
            "product_name_contains": "Topps"  # May extract product or use "Topps Order" fallback
        }
    },
    {
        "name": "topps_canceled_order",
        "subject": CANCELED_SUBJECT,
        "body": CANCELED_BODY,
        "expected": {
            "order_number": "US-12857405-S",
            "status": "Cancelled",
            "product_name_contains": "Topps"
        }
    },
    {
        "name": "topps_shipped_order",
        "subject": SHIPPED_SUBJECT,
        "body": SHIPPED_BODY,
        "expected": {
            "order_number": "US-12345678-S",
            "status": "Shipped",
            "product_name_contains": "Topps"
        }
    }
]
