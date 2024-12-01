# tests/test_app.py

import unittest
import json
from customer import app, Customer  # Adjust the import based on your app structure
from db_config import db
class CustomerAPITestCase(unittest.TestCase):
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

    def test_register_customer(self):
        """Test customer registration."""
        response = self.client.post('/customers/register', json={
            "fullname": "John Doe",
            "username": "johndoe123",
            "password": "securepassword",
            "age": 30,
            "address": "123 Main St, Anytown, USA",
            "gender": "Male",
            "marital_status": "Single"
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'Customer registered successfully', response.data)

    def test_delete_customer(self):
        """Test deleting a customer."""
        self.client.post('/customers/register', json={
            "fullname": "John Doe",
            "username": "johndoe123",
            "password": "securepassword",
            "age": 30,
            "address": "123 Main St, Anytown, USA",
            "gender": "Male",
            "marital_status": "Single"
        })
        response = self.client.delete('/customers/johndoe123/delete')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Customer deleted successfully', response.data)

    def test_update_customer(self):
        """Test updating customer information."""
        self.client.post('/customers/register', json={
            "fullname": "John Doe",
            "username": "johndoe123",
            "password": "securepassword",
            "age": 30,
            "address": "123 Main St, Anytown, USA",
            "gender": "Male",
            "marital_status": "Single"
        })
        response = self.client.put('/customers/johndoe123/update', json={
            "fullname": "John Smith",
            "age": 31
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Customer information updated successfully', response.data)

    def test_get_all_customers(self):
        """Test retrieving all customers."""
        self.client.post('/customers/register', json={
            "fullname": "John Doe",
            "username": "johndoe123",
            "password": "securepassword",
            "age": 30,
            "address": "123 Main St, Anytown, USA",
            "gender": "Male",
            "marital_status": "Single"
        })
        response = self.client.get('/customers')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'johndoe123', response.data)

    def test_charge_customer_wallet(self):
        """Test charging a customer's wallet."""
        self.client.post('/customers/register', json={
            "fullname": "John Doe",
            "username": "johndoe123",
            "password": "securepassword",
            "age": 30,
            "address": "123 Main St, Anytown, USA",
            "gender": "Male",
            "marital_status": "Single"
        })
        response = self.client.post('/customers/johndoe123/charge', json={"amount": 50.0})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account charged successfully', response.data)

    def test_deduct_from_wallet(self):
        """Test deducting from a customer's wallet."""
        self.client.post('/customers/register', json={
            "fullname": "John Doe",
            "username": "johndoe123",
            "password": "securepassword",
            "age": 30,
            "address": "123 Main St, Anytown, USA",
            "gender": "Male",
            "marital_status": "Single"
        })
        # First, charge the wallet to have a balance to deduct from
        self.client.post('/customers/johndoe123/charge', json={"amount": 100.0})

        # Now, deduct from the wallet
        response = self.client.post('/customers/johndoe123/deduct', json={"amount": 50.0})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Amount deducted successfully', response.data)

        # Check the updated wallet balance
        customer_response = self.client.get('/customers/johndoe123')
        self.assertIn(b'wallet_balance', customer_response.data)
        self.assertIn(b'50.0', customer_response.data)  # Check if the balance is now 50.0

    def test_deduct_insufficient_balance(self):
        """Test deducting from a customer's wallet with insufficient balance."""
        self.client.post('/customers/register', json={
            "fullname": "John Doe",
            "username": "johndoe123",
            "password": "securepassword",
            "age": 30,
            "address": "123 Main St, Anytown, USA",
            "gender": "Male",
            "marital_status": "Single"
        })

        # Attempt to deduct more than the current balance
        response = self.client.post('/customers/johndoe123/deduct', json={"amount": 50.0})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Insufficient balance.', response.data)

if __name__ == '__main__':
    unittest.main()