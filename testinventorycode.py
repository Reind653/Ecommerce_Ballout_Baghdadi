# tests/test_inventory.py

import unittest
import json
from inventory import app, db, Product  # Adjust the import based on your app structure

class InventoryAPITestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test client and create a new database for testing."""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for tests
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_product(self):
        """Test adding a new product to the inventory."""
        response = self.client.post('/inventory/add', json={
            "name": "Laptop",
            "category": "Electronics",
            "price": 999.99,
            "description": "A high-performance laptop.",
            "stock_count": 10
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Product added successfully', response.data)




    def test_get_all_products(self):
        """Test retrieving all products in the inventory."""
        self.client.post('/inventory/add', json={
            "name": "Laptop",
            "category": "Electronics",
            "price": 999.99,
            "description": "A high-performance laptop.",
            "stock_count": 10
        })
        self.client.post('/inventory/add', json={
            "name": "Smartphone",
            "category": "Electronics",
            "price": 499.99,
            "description": "A latest model smartphone.",
            "stock_count": 20
        })
        response = self.client.get('/inventory')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Laptop', response.data)
        self.assertIn(b'Smartphone', response.data)

    def test_get_product_by_name(self):
        """Test retrieving a specific product by its name."""
        self.client.post('/inventory/add', json={
            "name": "Laptop",
            "category": "Electronics",
            "price": 999.99,
            "description": "A high-performance laptop.",
            "stock_count": 10
        })
        response = self.client.get('/inventory/Laptop')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Laptop', response.data)

    def test_get_nonexistent_product(self):
        """Test retrieving a product that does not exist."""
        response = self.client.get('/inventory/NonExistentProduct')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Product not found.', response.data)

if __name__ == '__main__':
    unittest.main()