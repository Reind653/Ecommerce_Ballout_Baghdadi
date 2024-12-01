import pytest
from sales import app,Product
from customer import Customer
from db_config import db
import unittest

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for tests
    with app.app_context():
        db.create_all()
        
        # Add a sample customer without initializing the wallet balance
        customer = Customer(
            fullname="John Doe",
            username="johndoe",
            password="password123",
            age=30,
            address="123 Main St",
            gender="Male",
            marital_status="Single"
        )
        db.session.add(customer)
        
        # Add a sample product
        product = Product(
            name="Test Product",
            category="Test Category",
            price=10.00,
            description="A product for testing.",
            stock_count=100
        )
        db.session.add(product)
        db.session.commit()
        
        yield app.test_client()
        db.drop_all()

def test_display_available_goods(client):
    response = client.get('/sales/display')
    assert response.status_code == 200
    assert len(response.get_json()) > 0  # Ensure there is at least one product

def test_get_product_details(client):
    product = Product.query.first()
    response = client.get(f'/sales/product/{product.product_id}')
    assert response.status_code == 200
    assert product.name in response.get_json()["name"]

def test_purchase_product(client):
    # First, add funds to the customer's wallet using a hypothetical function
    customer = Customer.query.filter_by(username="johndoe").first()
    customer.wallet_balance = 100.00  # Add funds to the wallet
    db.session.commit()

    response = client.post('/sales/purchase', json={
        "username": "johndoe",
        "product_id": Product.query.first().product_id,
        "quantity": 5
    })
    assert response.status_code == 200
    assert "Purchase successful" in response.get_json()["message"]

def test_purchase_product_insufficient_funds(client):
    # Set the customer's wallet balance to a low amount using a hypothetical function
    customer = Customer.query.filter_by(username="johndoe").first()
    customer.wallet_balance = 5.00  # Set a low balance
    db.session.commit()

    response = client.post('/sales/purchase', json={
        "username": "johndoe",
        "product_id": Product.query.first().product_id,
        "quantity": 1
    })
    assert response.status_code == 400
    assert "Insufficient funds." in response.get_json()["message"]

def test_purchase_product_insufficient_stock(client):
    # First, add funds to the customer's wallet
    customer = Customer.query.filter_by(username="johndoe").first()
    customer.wallet_balance = 100.00  # Add funds to the wallet
    db.session.commit()

    response = client.post('/sales/purchase', json={
        "username": "johndoe",
        "product_id": Product.query.first().product_id,
        "quantity": 200  # Requesting more than available stock
    })
    assert response.status_code == 400
    assert "Not enough stock available." in response.get_json()["message"]

def test_get_purchase_history(client):
    # First, add funds to the customer's wallet
    customer = Customer.query.filter_by(username="johndoe").first()
    customer.wallet_balance = 100.00  # Add funds to the wallet
    db.session.commit()

    response = client.get('/sales/history/johndoe')
    assert response.status_code == 200
    assert "Showing purchase history for johndoe" in response.get_json()["message"]

def test_get_purchase_history_nonexistent_customer(client):
    response = client.get('/sales/history/nonexistent')
    assert response.status_code == 404
    assert "Customer not found." in response.get_json()["message"]

if __name__ == '__main__':
    unittest.main()