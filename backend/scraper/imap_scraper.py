"""
IMAP Email Scraper Module - Costco Orders

Connects to an IMAP server and scrapes Costco order emails.
"""

from imapclient import IMAPClient
from email import message_from_bytes
from email.header import decode_header
import re
from typing import List, Dict, Any
from html.parser import HTMLParser


class HTMLTextExtractor(HTMLParser):
    """Extract text from HTML content."""
    def __init__(self):
        super().__init__()
        self.text_parts = []
        
    def handle_data(self, data):
        self.text_parts.append(data)
    
    def get_text(self):
        return ' '.join(self.text_parts)


def html_to_text(html: str) -> str:
    """Convert HTML to plain text."""
    parser = HTMLTextExtractor()
    try:
        parser.feed(html)
        return parser.get_text()
    except:
        return html


def decode_email_header(header: Any) -> str:
    """Decode email header to string."""
    if header is None:
        return ""
    
    decoded_parts = decode_header(str(header))
    result = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result += part.decode(encoding or 'utf-8', errors='replace')
        else:
            result += str(part)
    return result


def parse_costco_email(subject: str, body: str, debug: bool = False) -> Dict[str, Any] | None:
    """
    Parse a Costco order email.
    
    Subject patterns:
    - "Your Costco.com Order Number 1261326992 Was Shipped"
    - "Your Costco.com Order Number 1261457232 is Confirmed"
    - "Your Costco.com Order #1261580310 Was Cancelled"
    
    Returns dict with: order_number, status, product_name, tracking_number
    """
    subject_lower = subject.lower()
    body_lower = body.lower()
    
    if debug:
        print(f"[DEBUG] Parsing email with subject: {subject[:80]}...")
    
    # Check if this is a Costco order email - be more flexible
    is_costco_order = (
        'costco.com order' in subject_lower or
        'costco.com' in subject_lower and 'order' in subject_lower or
        'order' in subject_lower and ('shipped' in subject_lower or 'confirmed' in subject_lower or 'cancel' in subject_lower or 'deliver' in subject_lower)
    )
    
    if not is_costco_order:
        if debug:
            print(f"[DEBUG] Skipped - not a Costco order email")
        return None
    
    # Extract order number from subject - try multiple patterns
    order_number = None
    
    # Pattern 1: "Order Number XXXXXXXXXX" or "Order #XXXXXXXXXX"
    order_match = re.search(r'order\s*(?:number|#)?\s*[:\s]?\s*(\d{8,12})', subject, re.IGNORECASE)
    if order_match:
        order_number = order_match.group(1)
    
    # Pattern 2: Just find any 10-digit number in subject (Costco order numbers are 10 digits)
    if not order_number:
        order_match = re.search(r'\b(\d{10})\b', subject)
        if order_match:
            order_number = order_match.group(1)
    
    # Pattern 3: Try in body
    if not order_number:
        order_match = re.search(r'order\s*(?:number|#)?\s*[:\s]?\s*(\d{8,12})', body, re.IGNORECASE)
        if order_match:
            order_number = order_match.group(1)
    
    if not order_number:
        if debug:
            print(f"[DEBUG] Skipped - no order number found in: {subject[:60]}")
        return None
    
    if debug:
        print(f"[DEBUG] Found order number: {order_number}")
    
    # Determine status from subject
    status = 'Unknown'
    if 'shipped' in subject_lower or 'has shipped' in subject_lower:
        status = 'Shipped'
    elif 'confirmed' in subject_lower or 'is confirmed' in subject_lower:
        status = 'Confirmed'
    elif 'cancelled' in subject_lower or 'canceled' in subject_lower:
        status = 'Cancelled'
    elif 'delivered' in subject_lower or 'has been delivered' in subject_lower:
        status = 'Delivered'
    
    # Convert HTML to clean text for easier parsing (used by multiple sections below)
    clean_body = html_to_text(body) if '<html' in body.lower() else body
    
    # Extract product name from body
    # Costco emails have product names in HTML divs before "X item from Costco"
    product_name = None
    
    # Pattern 1: Look for product name in image alt attribute (Costco emails use this)
    # Example: alt="AirPods 4 with Active Noise Cancellation"
    alt_pattern = r'alt="([^"]{10,100})"'
    alt_matches = re.findall(alt_pattern, body)
    for alt_text in alt_matches:
        alt_lower = alt_text.lower()
        # Skip generic/logo alt texts
        skip_texts = ['costco', 'logo', 'image', 'icon', 'banner', 'wholesale', 'header', 'footer', 'email']
        if any(skip in alt_lower for skip in skip_texts):
            continue
        # Check if it looks like a product name (contains product keywords)
        product_keywords = ['airpods', 'ipad', 'iphone', 'apple', 'watch', 'macbook', 'pro', 'max', 'gb', 'tb', 'inch', 'chip', 'wifi', 'wi-fi', 'cancellation', 'noise', 'silver', 'gold', 'black', 'white', 'blue']
        if any(kw in alt_lower for kw in product_keywords):
            product_name = alt_text.strip()
            product_name = product_name.replace('&amp;', '&').replace('&nbsp;', ' ')
            break
    
    # Pattern 2: Look for text right before "item from Costco" in HTML (fallback)
    if not product_name:
        costco_item_patterns = [
            r'>([^<]{10,100})</div>[^<]*<div[^>]*>\s*\d+\s*items?\s*from\s*Costco',
            r'>([^<]{10,100})</div>.*?\d+\s*items?\s*from\s*Costco',
            r'class="[^"]*P88qxe[^"]*">([^<]+)</div>',
        ]
        
        for pattern in costco_item_patterns:
            match = re.search(pattern, body, re.IGNORECASE | re.DOTALL)
            if match:
                product_name = match.group(1).strip()
                product_name = product_name.replace('&amp;', '&').replace('&nbsp;', ' ')
                product_name = re.sub(r'\s+', ' ', product_name)
                if len(product_name) > 5 and not product_name.startswith('http'):
                    break
                else:
                    product_name = None
    
    # Pattern 2: Try looking for product name patterns in plain text version
    if not product_name:
        # Look for lines that look like product names (contain product-like words)
        product_patterns = [
            r'(AirPods[^,\n]{0,50})',
            r'(iPad[^,\n]{0,50})',
            r'(iPhone[^,\n]{0,50})',
            r'(Apple Watch[^,\n]{0,50})',
            r'(MacBook[^,\n]{0,50})',
            r'([A-Z][A-Za-z0-9\s\-\(\),]{15,60}?)(?:\s+\$[\d,]+)',
        ]
        
        for pattern in product_patterns:
            match = re.search(pattern, clean_body)
            if match:
                product_name = match.group(1).strip()
                product_name = re.sub(r'\s+', ' ', product_name)
                if len(product_name) > 5:
                    break
    
    # Pattern 3: Fallback - look for any text between divs that's product-like
    if not product_name:
        # Try to find any substantial text in divs
        div_text_pattern = r'>([A-Z][^<]{15,80}(?:AirPods|iPad|iPhone|Watch|MacBook|GB|inch|chip)[^<]{0,30})</div>'
        match = re.search(div_text_pattern, body)
        if match:
            product_name = match.group(1).strip()
            product_name = re.sub(r'\s+', ' ', product_name)
    
    # Pattern 4: Try more aggressive search - any div with substantial product-like text
    if not product_name:
        # Look for divs with product keywords
        product_keywords = ['AirPods', 'iPad', 'iPhone', 'Apple', 'Watch', 'MacBook', 'Pro', 'Max', 'Mini', 'GB', 'TB', 'inch']
        for keyword in product_keywords:
            pattern = rf'>([^<]*{keyword}[^<]*)</div>'
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                # Make sure it's a reasonable product name (not too short, not HTML)
                if len(candidate) > 10 and len(candidate) < 100 and '<' not in candidate:
                    product_name = candidate
                    product_name = re.sub(r'\s+', ' ', product_name)
                    break
    
    # Debug: If still no product name, log the order number
    if not product_name and debug:
        print(f"[DEBUG] No product name found for order {order_number}")
    
    # Extract tracking number (if shipped or delivered)
    tracking_number = None
    if status in ['Shipped', 'Delivered']:
        tracking_patterns = [
            r'tracking\s*(?:number|#)?[:\s]+([A-Z0-9]{10,30})',
            r'track\s+your\s+(?:package|order)[:\s]+([A-Z0-9]{10,30})',
            r'(?:ups|fedex|usps)[:\s]+([A-Z0-9]{10,30})',
            r'1Z[A-Z0-9]{16}',  # UPS tracking format
            r'\b(\d{12,22})\b',  # FedEx/USPS numeric tracking
        ]
        
        for pattern in tracking_patterns:
            match = re.search(pattern, clean_body, re.IGNORECASE)
            if match:
                tracking_number = match.group(1) if match.lastindex else match.group(0)
                break
    
    return {
        'order_number': order_number,
        'status': status,
        'product_name': product_name or 'Unknown Product',
        'tracking_number': tracking_number
    }


def scrape_costco_orders(
    email: str,
    password: str,
    imap_host: str = 'imap.gmail.com',
    imap_port: int = 993,
    folder: str = 'INBOX',
    limit: int = 10000,  # High limit to capture all emails in folder
    debug: bool = True
) -> Dict[str, Any]:
    """
    Connect to IMAP server and scrape Costco order emails.
    
    Returns dict with:
        - orders: List of order dicts
        - stats: Overview stats (total, confirmed, shipped, cancelled)
    """
    orders = []
    seen_orders = {}  # Track orders by order_number to get latest status
    
    try:
        with IMAPClient(imap_host, port=imap_port, ssl=True) as client:
            # Login
            client.login(email, password)
            print(f"[INFO] Logged in successfully as {email}")
            
            # Select folder
            client.select_folder(folder, readonly=True)
            print(f"[INFO] Selected folder: {folder}")
            
            # Search for emails - if in INBOX, filter by Costco; otherwise get all
            if folder == 'INBOX':
                messages = client.search(['FROM', 'costco.com'])
            else:
                # Assume folder is already filtered (e.g., "A 2026 Costco Airpods")
                messages = client.search(['ALL'])
            
            print(f"[INFO] Found {len(messages)} emails in folder")
            
            # Get emails (most recent first)
            recent_messages = messages[-limit:] if len(messages) > limit else messages
            
            # Fetch email data
            if recent_messages:
                fetched = client.fetch(recent_messages, ['ENVELOPE', 'BODY[]', 'INTERNALDATE'])
                
                for uid, message_data in fetched.items():
                    try:
                        envelope = message_data[b'ENVELOPE']
                        raw_email = message_data[b'BODY[]']
                        date = message_data[b'INTERNALDATE']
                        
                        # Parse email
                        msg = message_from_bytes(raw_email)
                        
                        # Get subject
                        subject = decode_email_header(envelope.subject) if envelope.subject else ''
                        
                        # Get body (try HTML first, then plain text)
                        body = ''
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                if content_type == 'text/html':
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        body = payload.decode('utf-8', errors='replace')
                                        break
                                elif content_type == 'text/plain' and not body:
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        body = payload.decode('utf-8', errors='replace')
                        else:
                            payload = msg.get_payload(decode=True)
                            if payload:
                                body = payload.decode('utf-8', errors='replace')
                        
                        # Print email info for debugging
                        email_date = date.strftime('%Y-%m-%d') if date else 'Unknown'
                        print(f"[EMAIL] {email_date} | {subject[:60]}...")
                        
                        # Parse Costco order info
                        order_info = parse_costco_email(subject, body, debug=debug)
                        
                        if order_info:
                            print(f"  -> Matched! Order #{order_info['order_number']} - {order_info['status']}")
                            order_num = order_info['order_number']
                            order_date = date.isoformat() if date else ''
                            
                            order_data = {
                                'id': str(uid),
                                'order_number': order_num,
                                'product_name': order_info['product_name'],
                                'status': order_info['status'],
                                'tracking_number': order_info['tracking_number'],
                                'date': order_date,
                                'subject': subject[:100]
                            }
                            
                            # Keep track of orders - update if we find a newer status
                            # (e.g., Shipped replaces Confirmed for same order)
                            if order_num not in seen_orders:
                                seen_orders[order_num] = order_data
                            else:
                                # Update with newer info if this email is more recent
                                existing = seen_orders[order_num]
                                # Priority: Delivered > Shipped > Cancelled > Confirmed
                                status_priority = {'Confirmed': 1, 'Cancelled': 2, 'Shipped': 3, 'Delivered': 4, 'Unknown': 0}
                                if status_priority.get(order_info['status'], 0) > status_priority.get(existing['status'], 0):
                                    seen_orders[order_num] = order_data
                                # Also update tracking if we found it
                                if order_info['tracking_number'] and not seen_orders[order_num]['tracking_number']:
                                    seen_orders[order_num]['tracking_number'] = order_info['tracking_number']
                    
                    except Exception as e:
                        print(f"Error processing email {uid}: {e}")
                        continue
            
            client.logout()
    
    except Exception as e:
        raise Exception(f"IMAP connection failed: {str(e)}")
    
    # Convert to list and sort by date (most recent first)
    orders = list(seen_orders.values())
    orders.sort(key=lambda x: x['date'], reverse=True)
    
    # Calculate stats
    stats = {
        'total': len(orders),
        'confirmed': sum(1 for o in orders if o['status'] == 'Confirmed'),
        'shipped': sum(1 for o in orders if o['status'] == 'Shipped'),
        'delivered': sum(1 for o in orders if o['status'] == 'Delivered'),
        'cancelled': sum(1 for o in orders if o['status'] == 'Cancelled')
    }
    
    return {
        'orders': orders,
        'stats': stats
    }


# Keep the generic scraper for other vendors
def scrape_emails(
    email: str,
    password: str,
    imap_host: str = 'imap.gmail.com',
    imap_port: int = 993,
    folder: str = 'INBOX',
    limit: int = 100
) -> List[Dict[str, Any]]:
    """Generic email scraper - delegates to Costco scraper for now."""
    result = scrape_costco_orders(email, password, imap_host, imap_port, folder, limit)
    return result['orders']
