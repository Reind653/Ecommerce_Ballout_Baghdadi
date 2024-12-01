import unittest
from db_config import db
from customer import Customer
from inventory import Product
from reviews import app, Review

class ReviewsAPITestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test client and create a new database for testing."""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for tests
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            # Add sample data for testing
            self.customer = Customer(
                username='testuser',
                fullname='Test User',
                password='password123',
                age=30,
                address='123 Test St',
                gender='Other',
                marital_status='Single'
            )
            self.product = Product(
                name='Laptop',
                price=999.99,
                stock_count=10,
                category='Tech',
                description='high tech'
            )
            db.session.add(self.customer)
            db.session.add(self.product)
            db.session.commit()  # Commit to ensure they are saved in the database

    def tearDown(self):
        """Clean up after each test."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_add_review(self):
        """Test adding a review for a product."""
        # Re-fetch the product and customer to ensure they are bound to the session
        with self.app.app_context():
            customer = Customer.query.filter_by(username='testuser').first()
            product = Product.query.first()  # Assuming there's only one product for simplicity

            response = self.client.post('/reviews/submit', json={
                "username": customer.username,
                "product_id": product.product_id,  # Use the actual ID of the product
                "rating": 5,
                "comment": "Great product!"
            })
            self.assertEqual(response.status_code, 201)
            self.assertIn(b'Review submitted successfully', response.data)

    def test_get_reviews(self):
        """Test retrieving reviews for a product."""
        # Re-fetch the product and customer to ensure they are bound to the session
        with self.app.app_context():
            customer = Customer.query.filter_by(username='testuser').first()
            product = Product.query.first()  # Assuming there's only one product for simplicity

            # First, add a review
            self.client.post('/reviews/submit', json={
                "username": customer.username,
                "product_id": product.product_id,
                "rating": 5,
                "comment": "Great product!"
            })
            response = self.client.get(f'/reviews/product/{product.product_id}')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Great product!', response.data)

if __name__ == '__main__':
    unittest.main()