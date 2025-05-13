import unittest
import os
import io
import json
from unittest.mock import patch, MagicMock
from agent_app import create_app
from agent_app.src.services import ReceiptExtraction
from agent_app.src.models import db, ReceiptDetail, ReceiptItem

class TestReceiptExtraction(unittest.TestCase):
    """Test case for the receipt extraction functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = create_app(test_config={'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:'})
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def create_test_image(self, filename="test_receipt.jpg"):
        """Create a test image file"""
        image_content = b'fake image data'
        return io.BytesIO(image_content), filename
    
    def test_allowed_file(self):
        """Test file extension validation"""
        service = ReceiptExtraction()
        
        # Test allowed extensions
        self.assertTrue(service.allowed_file('receipt.jpg'))
        self.assertTrue(service.allowed_file('receipt.jpeg'))
        self.assertTrue(service.allowed_file('receipt.png'))
        
        # Test disallowed extensions
        self.assertFalse(service.allowed_file('receipt.pdf'))
        self.assertFalse(service.allowed_file('receipt.txt'))
        self.assertFalse(service.allowed_file('receipt'))
    
    def test_invalid_file_type(self):
        """Test extraction with invalid file type"""
        # Create an invalid file type
        test_file = MagicMock()
        test_file.filename = "receipt.pdf"
        
        # Call service
        service = ReceiptExtraction()
        result = service.extract_receipt_details(test_file)
        
        # Verify rejection
        self.assertEqual(result["status"], "error")
        self.assertIn("Invalid file type", result["message"])
        
        # Verify no database entry
        receipt = ReceiptDetail.query.first()
        self.assertIsNone(receipt)
    
    def test_api_endpoint_no_file(self):
        """Test the API endpoint with no file in request"""
        # Make request with no file
        response = self.client.post('/api/extract-receipt-details')
        
        # Check response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "error")
        self.assertIn("No file part", data["message"])
    
    def test_extraction_service_methods(self):
        """Test extract_receipt_details functionality with mocks"""
        # Create a subclass that overrides the AI methods for testing
        class TestReceiptExtractionService(ReceiptExtraction):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # Skip actual API client initialization
                self.client = None
            
            def _call_ai_model(self, file_path, base64_image):
                """Mock AI model call"""
                # For successful case
                if getattr(self, 'test_mode', None) == 'success':
                    return json.dumps({
                        "date": "2023-06-15",
                        "currency": "USD",
                        "vendor_name": "Test Store",
                        "receipt_items": [
                            {"item_name": "Item 1", "item_cost": 10.99},
                            {"item_name": "Item 2", "item_cost": 5.99}
                        ],
                        "tax": 1.50,
                        "total": 18.48
                    })
                # For invalid JSON case
                elif getattr(self, 'test_mode', None) == 'invalid_json':
                    return "This is not valid JSON"
                # For missing fields case
                elif getattr(self, 'test_mode', None) == 'missing_fields':
                    return json.dumps({
                        "date": "2023-06-15",
                        "vendor_name": "Test Store"
                        # Missing fields
                    })
                return "{}"
        
        # Split this into three separate tests to avoid database state issues
        self._test_successful_extraction(TestReceiptExtractionService)
        
        # Reset database completely between tests
        db.session.close()
        db.drop_all()
        db.create_all()
        
        self._test_invalid_json(TestReceiptExtractionService)
        
        # Reset database completely between tests
        db.session.close()
        db.drop_all()
        db.create_all()
        
        self._test_missing_fields(TestReceiptExtractionService)
    
    def _test_successful_extraction(self, TestReceiptExtractionService):
        """Test successful receipt extraction"""
        with patch('agent_app.src.services.os.makedirs'):
            with patch('agent_app.src.services.open'):
                with patch('agent_app.src.services.base64.b64encode') as mock_b64encode:
                    mock_b64encode.return_value = b'base64_encoded_data'
                    
                    mock_file = MagicMock()
                    mock_file.filename = "test_receipt.jpg"
                    
                    # Test successful case
                    service = TestReceiptExtractionService()
                    service.test_mode = 'success'
                    
                    with patch.object(service, '_save_image') as mock_save:
                        mock_save.return_value = ('test_path', '/static/path')
                        
                        result = service.extract_receipt_details(mock_file)
                        
                        # Assertions
                        self.assertEqual(result["status"], "success")
                        self.assertEqual(result["data"]["vendor_name"], "Test Store")
                        self.assertEqual(result["data"]["total"], 18.48)
                        self.assertEqual(len(result["data"]["receipt_items"]), 2)
                        
                        # Check database
                        receipt = ReceiptDetail.query.first()
                        self.assertIsNotNone(receipt)
                        self.assertEqual(receipt.vendor_name, "Test Store")
    
    def _test_invalid_json(self, TestReceiptExtractionService):
        """Test extraction with invalid JSON response"""
        with patch('agent_app.src.services.os.makedirs'):
            with patch('agent_app.src.services.open'):
                with patch('agent_app.src.services.base64.b64encode') as mock_b64encode:
                    mock_b64encode.return_value = b'base64_encoded_data'
                    
                    mock_file = MagicMock()
                    mock_file.filename = "test_receipt.jpg"
                    
                    # Test invalid JSON
                    service = TestReceiptExtractionService()
                    service.test_mode = 'invalid_json'
                    
                    with patch.object(service, '_save_image') as mock_save:
                        mock_save.return_value = ('test_path', '/static/path')
                        
                        result = service.extract_receipt_details(mock_file)
                        
                        # Assertions
                        self.assertEqual(result["status"], "error")
                        self.assertIn("Invalid JSON response", result["message"])
                        
                        # Check no database entry
                        receipt = ReceiptDetail.query.first()
                        self.assertIsNone(receipt)
    
    def _test_missing_fields(self, TestReceiptExtractionService):
        """Test extraction with missing fields in AI response"""
        with patch('agent_app.src.services.os.makedirs'):
            with patch('agent_app.src.services.open'):
                with patch('agent_app.src.services.base64.b64encode') as mock_b64encode:
                    mock_b64encode.return_value = b'base64_encoded_data'
                    
                    mock_file = MagicMock()
                    mock_file.filename = "test_receipt.jpg"
                    
                    # Test missing fields
                    service = TestReceiptExtractionService()
                    service.test_mode = 'missing_fields'
                    
                    with patch.object(service, '_save_image') as mock_save:
                        mock_save.return_value = ('test_path', '/static/path')
                        
                        result = service.extract_receipt_details(mock_file)
                        
                        # Assertions
                        self.assertEqual(result["status"], "error")
                        self.assertIn("Missing required field", result["message"])
                        
                        # Check no database entry
                        receipt = ReceiptDetail.query.first()
                        self.assertIsNone(receipt)

if __name__ == '__main__':
    unittest.main() 