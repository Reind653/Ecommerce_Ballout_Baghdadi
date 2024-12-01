import cProfile
import pstats
import io
from flask import Flask
from customer import app  # Import your Flask app

def run_profiling():
    pr = cProfile.Profile()
    pr.enable()  # Start profiling

    # Simulate requests to the Flask app
    with app.test_request_context():
        with app.test_client() as client:
            # Simulate a POST request to register a customer
            response = client.post('/customers/register', json={
                "fullname": "John Doe",
                "username": "johndoe",
                "password": "password123",
                "age": 30,
                "address": "123 Main St",
                "gender": "Male",
                "marital_status": "Single"
            })
            print("Register Customer Response:", response.get_json())

            # Simulate a GET request to retrieve all customers
            response = client.get('/customers')
            print("Get All Customers Response:", response.get_json())

            # Simulate a GET request to retrieve a specific customer
            response = client.get('/customers/johndoe')
            print("Get Customer by Username Response:", response.get_json())

            # Simulate a POST request to charge the customer's wallet
            response = client.post('/customers/johndoe/charge', json={"amount": 50.0})
            print("Charge Customer Wallet Response:", response.get_json())

            # Simulate a POST request to deduct from the customer's wallet
            response = client.post('/customers/johndoe/deduct', json={"amount": 20.0})
            print("Deduct from Customer Wallet Response:", response.get_json())

    pr.disable()  # Stop profiling

    # Save profiling results to a string
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s)
    ps.strip_dirs().sort_stats('cumulative').print_stats(10)  # Print top 10 functions by cumulative time

    # Print profiling results
    print(s.getvalue())

if __name__ == '__main__':
    run_profiling()