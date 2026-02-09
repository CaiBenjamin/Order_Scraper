from flask import Flask, request, jsonify
from flask_cors import CORS
from scraper import scrape_emails, scrape_costco_orders, scrape_topps_orders
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow requests from Next.js frontend

# Credentials from environment variables
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
IMAP_HOST = os.getenv('IMAP_HOST', 'imap.gmail.com')
IMAP_PORT = int(os.getenv('IMAP_PORT', '993'))

# Folder names for different vendors
COSTCO_FOLDER = os.getenv('COSTCO_FOLDER', 'A 2026 Costco Airpods')
TOPPS_FOLDER = os.getenv('TOPPS_FOLDER', 'INBOX')

# Gmail labels to search (exact names from /api/folders)
FOLDERS_TO_SEARCH = [
    COSTCO_FOLDER,  # From environment variable
]


@app.route('/api/costco', methods=['GET'])
def scrape_costco():
    """
    Endpoint to scrape Costco order emails.
    Uses hardcoded credentials for now.
    Searches multiple folders/labels.
    
    Returns:
        - orders: List of Costco orders with product name, status, tracking
        - stats: Overview (total, confirmed, shipped, cancelled)
    """
    all_orders = {}
    errors = []
    
    for folder in FOLDERS_TO_SEARCH:
        try:
            print(f"[INFO] Trying folder: {folder}")
            result = scrape_costco_orders(
                email=EMAIL,
                password=PASSWORD,
                imap_host=IMAP_HOST,
                imap_port=IMAP_PORT,
                folder=folder
            )
            
            # Merge orders (use order_number as key to avoid duplicates)
            for order in result['orders']:
                order_num = order['order_number']
                if order_num not in all_orders:
                    all_orders[order_num] = order
                else:
                    # Keep the one with higher status priority
                    status_priority = {'Confirmed': 1, 'Cancelled': 2, 'Shipped': 3, 'Delivered': 4}
                    existing_priority = status_priority.get(all_orders[order_num]['status'], 0)
                    new_priority = status_priority.get(order['status'], 0)
                    if new_priority > existing_priority:
                        all_orders[order_num] = order
            
            print(f"[INFO] Found {len(result['orders'])} orders in {folder}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"[WARN] Error with folder '{folder}': {error_msg}")
            errors.append(f"{folder}: {error_msg}")
            continue
    
    # Convert to list and sort
    orders_list = list(all_orders.values())
    orders_list.sort(key=lambda x: x['date'], reverse=True)
    
    # Calculate stats
    stats = {
        'total': len(orders_list),
        'confirmed': sum(1 for o in orders_list if o['status'] == 'Confirmed'),
        'shipped': sum(1 for o in orders_list if o['status'] == 'Shipped'),
        'delivered': sum(1 for o in orders_list if o['status'] == 'Delivered'),
        'cancelled': sum(1 for o in orders_list if o['status'] == 'Cancelled')
    }
    
    return jsonify({
        'success': True,
        'orders': orders_list,
        'stats': stats,
        'folders_searched': FOLDERS_TO_SEARCH,
        'errors': errors if errors else None
    })


@app.route('/api/topps', methods=['GET'])
def scrape_topps():
    """
    Endpoint to scrape Topps order emails.
    Uses hardcoded credentials for now.
    
    Returns:
        - orders: List of Topps orders with product name, status
        - stats: Overview (total, confirmed, shipped, cancelled)
    """
    try:
        print(f"[INFO] Scraping Topps orders from: {TOPPS_FOLDER}")
        result = scrape_topps_orders(
            email=EMAIL,
            password=PASSWORD,
            imap_host=IMAP_HOST,
            imap_port=IMAP_PORT,
            folder=TOPPS_FOLDER
        )
        
        return jsonify({
            'success': True,
            'orders': result['orders'],
            'stats': result['stats'],
            'folder_searched': TOPPS_FOLDER
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'orders': [],
            'stats': {'total': 0, 'confirmed': 0, 'shipped': 0, 'delivered': 0, 'cancelled': 0}
        }), 500


@app.route('/api/scrape', methods=['POST'])
def scrape_orders():
    """
    Generic endpoint to scrape order emails from user's inbox.
    
    Expected JSON body:
    {
        "email": "user@gmail.com",
        "password": "app-password",
        "imapHost": "imap.gmail.com",  (optional, defaults to gmail)
        "imapPort": 993                 (optional, defaults to 993)
    }
    """
    try:
        data = request.get_json(force=False, silent=False)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    try:
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        email = data.get('email')
        password = data.get('password')
        imap_host = data.get('imapHost', 'imap.gmail.com')
        imap_port = data.get('imapPort', 993)
        
        # Validate inputs
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Scrape emails for orders
        result = scrape_costco_orders(
            email=email,
            password=password,
            imap_host=imap_host,
            imap_port=int(imap_port)
        )
        
        return jsonify({
            'success': True,
            'orders': result['orders'],
            'stats': result['stats']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({'status': 'ok'})


@app.route('/api/debug/<order_number>', methods=['GET'])
def debug_order(order_number):
    """Debug endpoint to see raw email content for a specific order."""
    from imapclient import IMAPClient
    from email import message_from_bytes
    import re
    
    try:
        with IMAPClient(IMAP_HOST, port=IMAP_PORT, ssl=True) as client:
            client.login(EMAIL, PASSWORD)
            client.select_folder(FOLDERS_TO_SEARCH[0], readonly=True)
            
            # Search for emails containing this order number
            messages = client.search(['ALL'])
            
            for uid in messages:
                fetched = client.fetch([uid], ['ENVELOPE', 'BODY[]'])
                if uid in fetched:
                    envelope = fetched[uid][b'ENVELOPE']
                    raw_email = fetched[uid][b'BODY[]']
                    
                    subject = str(envelope.subject) if envelope.subject else ''
                    
                    if order_number in subject:
                        # Found it - return the raw HTML
                        from email import message_from_bytes
                        msg = message_from_bytes(raw_email)
                        
                        body = ''
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == 'text/html':
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        body = payload.decode('utf-8', errors='replace')
                                        break
                        else:
                            payload = msg.get_payload(decode=True)
                            if payload:
                                body = payload.decode('utf-8', errors='replace')
                        
                        # Find the section with product info
                        # Try multiple patterns
                        patterns = [
                            r'.{100}AirPods.{300}',
                            r'.{100}iPad.{300}',
                            r'.{100}item.{0,10}from.{0,10}Costco.{300}',
                            r'.{100}P88qxe.{300}',
                        ]
                        snippet = None
                        for pattern in patterns:
                            match = re.search(pattern, body, re.IGNORECASE | re.DOTALL)
                            if match:
                                snippet = match.group(0)
                                break
                        if not snippet:
                            snippet = body[:3000]
                        
                        return jsonify({
                            'success': True,
                            'order_number': order_number,
                            'subject': subject,
                            'snippet': snippet
                        })
            
            return jsonify({'error': f'Order {order_number} not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/folders', methods=['GET'])
def list_folders():
    """List all available Gmail folders/labels."""
    from imapclient import IMAPClient
    
    try:
        with IMAPClient(IMAP_HOST, port=IMAP_PORT, ssl=True) as client:
            client.login(EMAIL, PASSWORD)
            folders = client.list_folders()
            
            folder_names = []
            for flags, delimiter, name in folders:
                folder_names.append({
                    'name': name,
                    'flags': [f.decode() if isinstance(f, bytes) else str(f) for f in flags]
                })
            
            client.logout()
            
            return jsonify({
                'success': True,
                'folders': folder_names
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5000")
    print("Endpoints:")
    print("  GET  /api/costco - Scrape Costco orders (hardcoded credentials)")
    print("  GET  /api/topps  - Scrape Topps orders (hardcoded credentials)")
    print("  POST /api/scrape - Scrape order emails (custom credentials)")
    print("  GET  /api/health - Health check")
    app.run(debug=True, port=5000)
