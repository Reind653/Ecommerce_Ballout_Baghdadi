import cProfile
import pstats
import io
from flask import Flask
from inventory import app  # Import your Flask app

def run_profiling():
    pr = cProfile.Profile()
    pr.enable()  # Start profiling

    # Simulate requests to the Flask app
    with app.test_request_context():
        with app.test_client() as client:
            # Simulate a POST request to add a new product
            response = client.post('/inventory/add', json={
                "name": "Sample Product",
                "category": "Electronics",
                "price": 99.99,
                "description": "A sample electronic product.",
                "stock_count": 100
            })
            print("Add Product Response:", response.get_json())

            # Simulate a GET request to retrieve all products
            response = client.get('/inventory')
            print("Get All Products Response:", response.get_json())

            # Simulate a GET request to retrieve a specific product by name
            response = client.get('/inventory/Sample Product')
            print("Get Product by Name Response:", response.get_json())

            # Simulate a POST request to deduct stock from the product
            response = client.post('/inventory/Sample Product/deduct', json={"quantity": 10})
            print("Deduct Stock Response:", response.get_json())

            # Simulate a PUT request to update the product's details
            response = client.put('/inventory/Sample Product/update', json={
                "price": 89.99,
                "stock_count": 90
            })
            print("Update Product Response:", response.get_json())

    pr.disable()  # Stop profiling

    # Save profiling results to a string
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s)
    ps.strip_dirs().sort_stats('cumulative').print_stats(10)  # Print top 10 functions by cumulative time

    # Print profiling results
    print(s.getvalue())

if __name__ == '__main__':
    run_profiling()