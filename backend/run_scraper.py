"""
Standalone script to run the Costco order scraper.
Run with: python run_scraper.py
"""

from scraper import scrape_costco_orders
import json

# Configuration
EMAIL = "bencai45@gmail.com"
PASSWORD = "xuzo thvb ombv kadf"
FOLDER = "A 2026 Costco Airpods"

def main():
    print(f"Scraping Costco orders from '{FOLDER}'...")
    print("-" * 50)
    
    result = scrape_costco_orders(
        email=EMAIL,
        password=PASSWORD,
        folder=FOLDER
    )
    
    # Print stats
    stats = result['stats']
    print(f"\n📊 STATS:")
    print(f"   Total Orders:  {stats['total']}")
    print(f"   Confirmed:     {stats['confirmed']}")
    print(f"   Shipped:       {stats['shipped']}")
    print(f"   Delivered:     {stats['delivered']}")
    print(f"   Cancelled:     {stats['cancelled']}")
    
    # Print orders by status
    orders = result['orders']
    
    print(f"\n✅ CONFIRMED ORDERS ({stats['confirmed']}):")
    print("-" * 50)
    for order in orders:
        if order['status'] == 'Confirmed':
            print(f"  {order['order_number']} | {order['product_name'][:40]}")
    
    print(f"\n📦 SHIPPED ORDERS ({stats['shipped']}):")
    print("-" * 50)
    for order in orders:
        if order['status'] == 'Shipped':
            tracking = order['tracking_number'] or 'No tracking'
            print(f"  {order['order_number']} | {order['product_name'][:40]} | {tracking}")
    
    print(f"\n❌ CANCELLED ORDERS ({stats['cancelled']}):")
    print("-" * 50)
    for order in orders:
        if order['status'] == 'Cancelled':
            print(f"  {order['order_number']} | {order['product_name'][:40]}")
    
    # Optionally save to JSON
    with open('orders_output.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\n💾 Full results saved to orders_output.json")

if __name__ == '__main__':
    main()
