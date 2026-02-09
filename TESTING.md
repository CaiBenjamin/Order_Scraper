# Testing Guide

This document explains how to run tests locally and set up CI/CD with GitHub Actions.

## Running Tests Locally

### Backend Tests (Python/pytest)

1. Install test dependencies:
```bash
cd backend
pip install -r requirements-dev.txt
```

2. Run all tests:
```bash
pytest
```

3. Run tests with coverage:
```bash
pytest --cov=scraper --cov-report=term --cov-report=html
```

4. Run specific test file:
```bash
pytest tests/test_costco_parser.py -v
```

5. Run tests by marker:
```bash
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
```

### Frontend Tests (Next.js)

```bash
npm test
```

Currently, frontend tests are stubbed. To add full testing:
- Install Jest or Vitest
- Add `@testing-library/react` for component tests
- Create test files in `__tests__/` directories

## Test Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest configuration
│   ├── test_costco_parser.py      # Parser unit tests
│   ├── test_api.py                # API integration tests
│   └── fixtures/
│       ├── __init__.py
│       └── costco_emails.py       # Sample email data
└── pytest.ini                     # Pytest settings
```

## Test Coverage

The test suite covers:

### ✅ Parser Tests (`test_costco_parser.py`)
- Confirmed, Shipped, Cancelled, Delivered order emails
- Order number extraction (from subject and body)
- Product name extraction (alt attribute and fallback methods)
- Tracking number extraction
- Status detection
- HTML entity decoding
- Edge cases (empty inputs, malformed HTML, etc.)

### ✅ API Tests (`test_api.py`)
- Health check endpoint
- Scraper endpoint validation
- JSON payload validation
- Error handling

### ✅ Integration Tests (in CI/CD)
- End-to-end parser functionality
- Security scan for hardcoded credentials
- Build verification for frontend

## GitHub Actions CI/CD

### What Gets Tested

Every push to `main` or `develop` triggers:

1. **Backend Tests**
   - Python 3.12 on Ubuntu
   - Pytest with coverage reporting
   - Results uploaded to Codecov

2. **Frontend Tests**
   - Node.js 20 on Ubuntu
   - Linting with ESLint
   - Build verification with Next.js

3. **Integration Tests**
   - End-to-end parser validation
   - Security scan for credentials

4. **Security Scan**
   - Checks for hardcoded credentials in code
   - Verifies `.env` is gitignored

### Setting Up GitHub Actions (Optional: For Live IMAP Tests)

If you want to run LIVE tests against your Gmail account in CI/CD:

1. Go to your GitHub repo: https://github.com/CaiBenjamin/Order_Scraper
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these secrets:

| Secret Name | Value |
|-------------|-------|
| `EMAIL` | Your Gmail address |
| `PASSWORD` | Your Gmail App Password |
| `IMAP_HOST` | `imap.gmail.com` |
| `IMAP_PORT` | `993` |
| `FOLDER` | `A 2026 Costco Airpods` |

⚠️ **Note:** The current workflow does NOT require these secrets. Tests use fixtures and don't connect to real IMAP servers.

### Workflow File

Location: `.github/workflows/ci.yml`

The workflow runs on:
- Push to `main` or `develop`
- Pull requests to `main`

## Adding New Tests

### Adding Backend Tests

1. Create a new test file in `backend/tests/`:
```python
# tests/test_new_feature.py
import pytest
from scraper.module import function_to_test

def test_my_feature():
    result = function_to_test()
    assert result == expected_value
```

2. Add test fixtures in `tests/fixtures/` if needed

3. Run: `pytest tests/test_new_feature.py`

### Adding Frontend Tests

1. Install testing libraries:
```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest
```

2. Create test files next to components:
```typescript
// app/components/__tests__/CredentialsForm.test.tsx
import { render, screen } from '@testing-library/react';
import CredentialsForm from '../CredentialsForm';

test('renders scraper button', () => {
  render(<CredentialsForm />);
  expect(screen.getByText(/Run Costco Scraper/i)).toBeInTheDocument();
});
```

3. Update `package.json` scripts to run tests

## Continuous Integration Status

You can add a badge to your README:

```markdown
![CI/CD](https://github.com/CaiBenjamin/Order_Scraper/workflows/CI/CD%20Pipeline/badge.svg)
```

## Test Commands Quick Reference

| Command | Description |
|---------|-------------|
| `pytest` | Run all backend tests |
| `pytest -v` | Verbose output |
| `pytest --cov=scraper` | With coverage |
| `pytest -m unit` | Only unit tests |
| `pytest -k test_parse` | Run tests matching name |
| `pytest --lf` | Re-run last failed tests |
| `npm test` | Run frontend tests |
| `npm run lint` | Run linter |
| `npm run build` | Verify build works |

## Debugging Failed Tests

1. **View detailed output:**
```bash
pytest -vv --tb=long
```

2. **Run a single test:**
```bash
pytest tests/test_costco_parser.py::TestCostcoEmailParser::test_parse_costco_email -vv
```

3. **Print debugging info:**
```python
def test_something():
    result = function()
    print(f"Result: {result}")  # Will show with -s flag
    assert result == expected
```

Run with: `pytest -s`

## Pre-commit Hooks (Optional)

Install pre-commit to run tests before committing:

```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

Install: `pre-commit install`

Now tests run automatically before every commit!
