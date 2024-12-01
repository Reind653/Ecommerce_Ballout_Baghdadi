import pytest
import json
from customer import app, Customer  # Adjust the import based on your actual app structure
from db_config import db

@pytest.fixture(scope='module')
def test_client():
    # Create a test client
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for testing
    with app.app_context():
        db.create_all()  # Create the database tables
        yield app.test_client()  # Provide the test client
        db.drop_all()  # Clean up after tests

def test_register_customer(test_client):
    response = test_client.post('/customers/register', json={
        "fullname": "John Doe",
        "username": "johndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "Male",
        "marital_status": "Single"
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == "Customer registered successfully"
    assert data['customer']['username'] == "johndoe"

def test_register_duplicate_username(test_client):
    # Try to register the same username again
    response = test_client.post('/customers/register', json={
        "fullname": "Jane Doe",
        "username": "johndoe",
        "password": "password456",
        "age": 25,
        "address": "456 Elm St",
        "gender": "Female",
        "marital_status": "Married"
    })
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['message'] == "Username already taken."

def test_get_all_customers(test_client):
    response = test_client.get('/customers')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)  # Should return a list

def test_get_customer_by_username(test_client):
    response = test_client.get('/customers/johndoe')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['username'] == "johndoe"

def test_update_customer(test_client):
    response = test_client.put('/customers/johndoe/update', json={
        "fullname": "Johnathan Doe",
        "age": 31
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['customer']['fullname'] == "Johnathan Doe"
    assert data['customer']['age'] == 31

def test_charge_customer_wallet(test_client):
    response = test_client.post('/customers/johndoe/charge', json={"amount": 100.0})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['wallet_balance'] == 100.0

def test_deduct_from_wallet(test_client):
    response = test_client.post('/customers/johndoe/deduct', json={"amount": 50.0})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['wallet_balance'] == 50.0

def test_delete_customer(test_client):
    response = test_client.delete('/customers/johndoe/delete')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == "Customer deleted successfully"

def test_get_deleted_customer(test_client):
    response = test_client.get('/customers/johndoe')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['message'] == "Customer not found."

# Run the tests if this file is executed directly
if __name__ == '__main__':
    pytest.main()