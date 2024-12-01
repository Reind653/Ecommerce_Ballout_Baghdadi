import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from reviews import app, db, Review
from customer import Customer  # Assuming Customer model is defined in customer.py
from inventory import Product  # Assuming Product model is defined in inventory.py

@pytest.fixture
def test_client():
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create the database tables
            yield client
            db.drop_all()  # Clean up after tests

@pytest.fixture
def setup_data(test_client):
    """Set up initial data for tests."""
    # Create a customer
    customer = Customer(username='testuser', password='password', fullname='Test User', 
                        age=30, address='123 Test St', gender='Other', marital_status='Single')
    db.session.add(customer)
    
    # Create a product
    product = Product(name='Test Product', category='Test Category', 
                      price=10.0, description='A test product', stock_count=100)
    db.session.add(product)
    
    db.session.commit()  # Commit changes to the database

    return customer, product

def test_submit_review_success(test_client, setup_data):
    """Test submitting a review successfully."""
    customer, product = setup_data
    response = test_client.post('/reviews/submit', json={
        'username': customer.username,
        'product_id': product.product_id,
        'rating': 5,
        'comment': 'Great product!'
    })
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Review submitted successfully'
    assert data['review']['rating'] == 5
    assert data['review']['comment'] == 'Great product!'

def test_submit_review_customer_not_found(test_client, setup_data):
    """Test submitting a review when the customer is not found."""
    product = setup_data[1]
    response = test_client.post('/reviews/submit', json={
        'username': 'nonexistentuser',
        'product_id': product.product_id,
        'rating': 5
    })
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Customer not found.'

def test_submit_review_product_not_found(test_client, setup_data):
    """Test submitting a review when the product is not found."""
    customer = setup_data[0]
    response = test_client.post('/reviews/submit', json={
        'username': customer.username,
        'product_id': 'nonexistentproduct',
        'rating': 5
    })
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Product not found.'

def test_update_review_success(test_client, setup_data):
    """Test updating an existing review."""
    customer, product = setup_data
    # First submit a review
    submit_response = test_client.post('/reviews/submit', json={
        'username': customer.username,
        'product_id': product.product_id,
        'rating': 4,
        'comment': 'Good product.'
    })
    review_id = submit_response.get_json()['review']['review_id']
    
    # Now update the review
    response = test_client.put(f'/reviews/update/{review_id}', json={
        'rating': 5,
        'comment': 'Excellent product!'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Review updated successfully'
    assert data['review']['rating'] == 5
    assert data['review']['comment'] == 'Excellent product!'

def test_update_review_not_found(test_client):
    """Test updating a review that does not exist."""
    response = test_client.put('/reviews/update/nonexistentreviewid', json={
        'rating': 5,
        'comment': 'This should not work.'
    })

    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Review not found.'

def test_delete_review_success(test_client, setup_data):
    """Test deleting a review."""
    customer, product = setup_data
    # First submit a review
    submit_response = test_client.post('/reviews/submit', json={
        'username': customer.username,
        'product_id': product.product_id,
        'rating': 3,
        'comment': 'Average product.'
    })
    review_id = submit_response.get_json()['review']['review_id']
    
    # Now delete the review
    response = test_client.delete(f'/reviews/delete/{review_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Review deleted successfully'

def test_delete_review_not_found(test_client):
    """Test deleting a review that does not exist."""
    response = test_client.delete('/reviews/delete/nonexistentreviewid')
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Review not found.'

def test_get_product_reviews(test_client, setup_data):
    """Test retrieving reviews for a specific product."""
    customer, product = setup_data
    # Submit a couple of reviews for the same product
    for rating, comment in [(5, 'Great!'), (4, 'Good product.')]:
        test_client.post('/reviews/submit', json={
            'username': customer.username,
            'product_id': product.product_id,
            'rating': rating,
            'comment': comment
        })

    response = test_client.get(f'/reviews/product/{product.product_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2  # We submitted two reviews
    assert all(review['product_id'] == product.product_id for review in data)

def test_get_customer_reviews(test_client, setup_data):
    """Test retrieving reviews submitted by a specific customer."""
    customer, product = setup_data
    # Submit a review for the customer
    test_client.post('/reviews/submit', json={
        'username': customer.username,
        'product_id': product.product_id,
        'rating': 5,
        'comment': 'Excellent product!'
    })

    response = test_client.get(f'/reviews/customer/{customer.username}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1  # We submitted one review
    assert data[0]['customer_id'] == customer.customer_id

def test_moderate_review_success(test_client, setup_data):
    """Test moderating a review."""
    customer, product = setup_data
    # Submit a review first
    submit_response = test_client.post('/reviews/submit', json={
        'username': customer.username,
        'product_id': product.product_id,
        'rating': 2,
        'comment': 'Not good.'
    })
    review_id = submit_response.get_json()['review']['review_id']
    
    # Moderate the review
    response = test_client.post(f'/reviews/moderate/{review_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Review moderated successfully'
    assert data['review']['moderated'] is True

def test_moderate_review_not_found(test_client):
    """Test moderating a review that does not exist."""
    response = test_client.post('/reviews/moderate/nonexistentreviewid')
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Review not found.'

def test_get_review_details_success(test_client, setup_data):
    """Test retrieving details for a specific review."""
    customer, product = setup_data
    # Submit a review first
    submit_response = test_client.post('/reviews/submit', json={
        'username': customer.username,
        'product_id': product.product_id,
        'rating': 4,
        'comment': 'Good product.'
    })
    review_id = submit_response.get_json()['review']['review_id']
    
    # Get review details
    response = test_client.get(f'/reviews/details/{review_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['review_id'] == review_id
    assert data['customer_username'] == customer.username
    assert data['product_name'] == product.name

def test_get_review_details_not_found(test_client):
    """Test retrieving details for a review that does not exist."""
    response = test_client.get('/reviews/details/nonexistentreviewid')
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Review not found.'

# Run the tests
if __name__ == '__main__':
    pytest.main()