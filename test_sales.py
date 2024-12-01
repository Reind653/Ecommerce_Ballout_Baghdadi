import pytest
from flask import Flask
from customer import Customer
from inventory import Product
from sales import app as sales_app
from db_config import db

@pytest.fixture(scope='module')
def test_client():
    """Create a test client for the Flask application."""
    with sales_app.test_client() as client:
        with sales_app.app_context():
            db.create_all()  # Create the database tables
            yield client
            db.drop_all()  # Drop the database tables after tests

@pytest.fixture(scope='module')
def setup_data(test_client):
    """Setup initial data for testing."""
    # Create a customer
    customer = Customer(fullname="Test User", username="testuser", password="password", age=30, address="123 Test St", gender="Other", marital_status="Single")
    db.session.add(customer)
    
    # Create a product
    product = Product(name="Test Product", category="Test Category", price=10.0, description="A test product", stock_count=100)
    db.session.add(product)
    
    db.session.commit()
    
    return customer, product

def test_display_available_goods(test_client, setup_data):
    """Test displaying available products."""
    response = test_client.get('/sales/display')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) > 0
    assert data[0]['name'] == setup_data[1].name  # Check if the product is in the response

def test_get_product_details(test_client, setup_data):
    """Test retrieving product details."""
    product_id = setup_data[1].product_id
    response = test_client.get(f'/sales/product/{product_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == setup_data[1].name

def test_purchase_product_success(test_client, setup_data):
    """Test successful product purchase."""
    # First, ensure the customer has a sufficient wallet balance
    customer = setup_data[0]  # Assuming setup_data[0] contains the customer object
    customer.wallet_balance = 100.0  # Set the initial balance to 100
    db.session.commit()  # Commit the change to the database

    # Print initial wallet balance for debugging
    print(f"Initial wallet balance: {customer.wallet_balance}")

    # Attempt to purchase a product
    response = test_client.post('/sales/purchase', json={
        'username': customer.username,
        'product_id': setup_data[1].product_id,  # Assuming setup_data[1] contains a valid product
        'quantity': 1
    })

    # Print the response for debugging
    print(f"Response status code: {response.status_code}")
    print(f"Response data: {response.get_json()}")

    # Assertions to check if the purchase was successful
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Purchase successful'
    assert data['customer_wallet_balance'] == 90.0  # Wallet balance should be 100 - 10 (product price)

def test_purchase_product_customer_not_found(test_client):
    """Test purchasing a product with a non-existent customer."""
    response = test_client.post('/sales/purchase', json={
        'username': 'nonexistentuser',
        'product_id': 'some-product-id',
        'quantity': 1
    })
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Customer not found.'

def test_purchase_product_not_found(test_client, setup_data):
    """Test purchasing a product that does not exist."""
    response = test_client.post('/sales/purchase', json={
        'username': 'testuser',
        'product_id': 'invalid-product-id',
        'quantity': 1
    })
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Product not found.'

def test_purchase_insufficient_stock(test_client, setup_data):
    """Test purchasing a product with insufficient stock."""
    response = test_client.post('/sales/purchase', json={
        'username': 'testuser',
        'product_id': setup_data[1].product_id,
        'quantity': 200  # More than available
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Not enough stock available.'

def test_purchase_insufficient_funds(test_client, setup_data):
    """Test purchasing a product with insufficient funds."""
    # Set the customer's wallet balance to a low amount
    setup_data[0].wallet_balance = 5.0
    db.session.commit()

    response = test_client.post('/sales/purchase', json={
        'username': 'testuser',
        'product_id': setup_data[1].product_id,
        'quantity': 1  # The cost is 10.0, which is more than the available balance
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Insufficient funds.'

def test_purchase_missing_fields(test_client):
    """Test purchasing a product with missing required fields."""
    response = test_client.post('/sales/purchase', json={
        'username': 'testuser',
        'quantity': 1  # Missing product_id
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'product_id is required.'

def test_get_purchase_history(test_client, setup_data):
    """Test retrieving purchase history for a valid customer."""
    response = test_client.get('/sales/history/testuser')
    assert response.status_code == 200
    data = response.get_json()
    assert data['customer']['username'] == 'testuser'

def test_get_purchase_history_customer_not_found(test_client):
    """Test retrieving purchase history for a non-existent customer."""
    response = test_client.get('/sales/history/nonexistentuser')
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Customer not found.'
   
# Run the tests if this file is executed
if __name__ == '__main__':
    pytest.main()