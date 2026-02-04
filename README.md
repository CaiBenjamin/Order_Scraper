# Costco Order Scraper

A web application to scrape and track Costco orders from Gmail using IMAP. Built with Next.js (frontend) and Flask (backend).

## Features

- 📧 Connect to Gmail via IMAP to scrape Costco order emails
- 📊 Dashboard with order statistics (Total, Confirmed, Shipped, Delivered, Cancelled)
- 🔍 Search and filter orders by product, order number, tracking number, or status
- 🎨 Modern UI with dark mode support
- 🔒 Secure credential handling via environment variables

## Architecture

```
Frontend (Next.js) → Backend (Flask) → Gmail IMAP → Costco Emails
  Port 3000            Port 5000
```

## Setup

### Prerequisites

- Python 3.12+
- Node.js 20+
- Gmail account with App Password enabled

### Backend Setup

1. Navigate to backend folder:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file in `backend/` directory:
```bash
EMAIL=your-email@gmail.com
PASSWORD=your-app-password
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
FOLDER=A 2026 Costco Airpods
```

4. Start Flask server:
```bash
python app.py
```

Server runs on http://localhost:5000

### Frontend Setup

1. Install Node dependencies:
```bash
npm install
```

2. Start Next.js dev server:
```bash
npm run dev
```

Frontend runs on http://localhost:3000

## Gmail App Password Setup

1. Enable 2-factor authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Create an app password
4. Use that password in your `.env` file (not your regular Gmail password)

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/costco` | Scrape Costco orders (uses .env credentials) |
| POST | `/api/scrape` | Scrape with custom credentials (JSON body) |
| GET | `/api/health` | Health check |
| GET | `/api/debug/<order_number>` | Debug specific order email HTML |
| GET | `/api/folders` | List all Gmail folders/labels |

## Project Structure

```
order_scraper_ui/
├── app/                          # Next.js frontend
│   ├── components/
│   │   └── CredentialsForm.tsx  # Main scraper UI component
│   ├── page.tsx                 # Home page
│   └── layout.tsx               # Root layout
├── backend/                      # Flask backend
│   ├── app.py                   # Flask server & routes
│   ├── .env                     # Credentials (gitignored)
│   ├── requirements.txt         # Python dependencies
│   ├── run_scraper.py           # Standalone scraper script
│   └── scraper/
│       ├── __init__.py
│       └── imap_scraper.py      # Costco email parsing logic
├── .gitignore
└── README.md
```

## Running Standalone Scraper

You can run the scraper without the web UI:

```bash
cd backend
python run_scraper.py
```

This outputs results to console and saves to `orders_output.json`.

## Technologies

- **Frontend**: Next.js 16, React 19, Tailwind CSS 4, TypeScript
- **Backend**: Flask 3, Python 3.12
- **Email**: IMAPClient for Gmail IMAP connection
- **Parsing**: Regex for extracting order data from HTML emails

## Security Notes

- Never commit `.env` file (already in `.gitignore`)
- Use Gmail App Passwords, not your main password
- Backend credentials are loaded from environment variables only

## License

MIT
