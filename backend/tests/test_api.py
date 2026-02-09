"""
Integration tests for Flask API endpoints.
These tests verify that the API routes work correctly.
"""

import pytest
from app import app
import json


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Test the health check endpoint."""
    
    def test_health_check(self, client):
        """Test /api/health returns ok status."""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'


class TestScraperEndpoints:
    """Test scraper API endpoints (without actual IMAP connection)."""
    
    def test_costco_endpoint_exists(self, client):
        """Test that /api/costco endpoint exists."""
        # This will fail without credentials, but should return 500 not 404
        response = client.get('/api/costco')
        
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404
    
    def test_scrape_endpoint_requires_json(self, client):
        """Test that /api/scrape requires JSON body."""
        response = client.post('/api/scrape')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_scrape_endpoint_validates_credentials(self, client):
        """Test that /api/scrape validates required fields."""
        response = client.post(
            '/api/scrape',
            data=json.dumps({'email': 'test@example.com'}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'password' in data['error'].lower()


class TestDebugEndpoints:
    """Test debug and utility endpoints."""
    
    def test_folders_endpoint_exists(self, client):
        """Test that /api/folders endpoint exists."""
        response = client.get('/api/folders')
        
        # Should not be 404 (endpoint exists)
        # May fail with 500 due to missing credentials, but that's ok
        assert response.status_code != 404
    
    def test_debug_endpoint_format(self, client):
        """Test that /api/debug/<order_number> endpoint exists."""
        response = client.get('/api/debug/1234567890')
        
        # Should not be 404 (endpoint exists)
        assert response.status_code != 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
