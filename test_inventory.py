import pytest
import json
from inventory import app, Product  # Assuming your main app file is named app.py
from db_config import db
@pytest.fixture
def client():
    """A test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()  # Create tables
        yield app.test_client()  # Provide the test client
        db.drop_all()  # Cleanup after tests

def test_add_product(client):
    """Test adding a product."""
    response = client.post('/inventory/add', json={
        'name': 'Test Product',
        'category': 'food',
        'price': 10.99,
        'description': 'A test product',
        'stock_count': 100
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Product added successfully'
    assert data['product']['name'] == 'Test Product'

def test_update_product(client):
    """Test updating a product."""
    # First, add a product to update
    response = client.post('/inventory/add', json={
        'name': 'Test Product',
        'category': 'food',
        'price': 10.99,
        'description': 'A test product',
        'stock_count': 100
    })
    product_id = json.loads(response.data)['product']['product_id']

    # Now update the product
    response = client.put(f'/inventory/{product_id}/update', json={
        'price': 12.99,
        'stock_count': 80
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Product information updated successfully'
    assert data['product']['price'] == 12.99
    assert data['product']['stock_count'] == 80

def test_deduct_product(client):
    """Test deducting stock from a product."""
    # First, add a product to deduct from
    response = client.post('/inventory/add', json={
        'name': 'Test Product',
        'category': 'food',
        'price': 10.99,
        'description': 'A test product',
        'stock_count': 100
    })
    product_id = json.loads(response.data)['product']['product_id']

    # Now deduct stock
    response = client.post(f'/inventory/{product_id}/deduct', json={
        'quantity': 20
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == '20 items deducted successfully.'
    assert data['product']['stock_count'] == 80

def test_get_all_products(client):
    """Test retrieving all products."""
    # Add a couple of products
    client.post('/inventory/add', json={
        'name': 'Product 1',
        'category': 'food',
        'price': 10.99,
        'description': 'A test product 1',
        'stock_count': 100
    })
    client.post('/inventory/add', json={
        'name': 'Product 2',
        'category': 'clothes',
        'price': 20.99,
        'description': 'A test product 2',
        'stock_count': 50
    })

    response = client.get('/inventory')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2

def test_get_product_by_name(client):
    """Test retrieving a product by name."""
    # Add a product
    client.post('/inventory/add', json={
        'name': 'Unique Product',
        'category': 'food',
        'price': 15.99,
        'description': 'A unique product',
        'stock_count': 50
    })

    response = client.get('/inventory/Unique Product')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['name'] == 'Unique Product'

def test_product_not_found(client):
    """Test retrieving a non-existent product."""
    response = client.get('/inventory/Non-Existent Product')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['message'] == 'Product not found.'

def test_deduct_insufficient_stock(client):
    """Test deducting more stock than available."""
    # Add a product with a specific stock count
    response = client.post('/inventory/add', json={
        'name': 'Test Product',
        'category': 'food',
        'price': 10.99,
        'description': 'A test product',
        'stock_count': 10
    })
    product_id = json.loads(response.data)['product']['product_id']

    # Attempt to deduct more stock than available
    response = client.post(f'/inventory/{product_id}/deduct', json={
        'quantity': 15
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['message'] == 'Not enough stock available.'

def test_deduct_zero_or_negative_quantity(client):
    """Test deducting zero or negative quantity."""
    # Add a product
    response = client.post('/inventory/add', json={
        'name': 'Test Product',
        'category': 'food',
        'price': 10.99,
        'description': 'A test product',
        'stock_count': 10
    })
    product_id = json.loads(response.data)['product']['product_id']

    # Attempt to deduct zero quantity
    response = client.post(f'/inventory/{product_id}/deduct', json={
        'quantity': 0
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['message'] == 'Quantity to deduct must be greater than zero.'

    # Attempt to deduct negative quantity
    response = client.post(f'/inventory/{product_id}/deduct', json={
        'quantity': -5
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['message'] == 'Quantity to deduct must be greater than zero.'

def test_update_non_existent_product(client):
    """Test updating a product that does not exist."""
    response = client.put('/inventory/non-existent-id/update', json={
        'price': 15.99
    })
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['message'] == 'Product not found.'

def test_add_product_missing_fields(client):
    """Test adding a product with missing required fields."""
    response = client.post('/inventory/add', json={
        'name': 'Incomplete Product',
        'category': 'food',
        # 'price' is missing
        'stock_count': 10
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['message'] == 'price is required.'

# Run the tests if this file is executed
if __name__ == '__main__':
    pytest.main()