import cProfile
import pstats
import io
from flask import Flask
from sales import app  # Import your Flask app

def run_profiling():
    pr = cProfile.Profile()
    pr.enable()  # Start profiling

    # Simulate requests to the Flask app
    with app.test_request_context():
        with app.test_client() as client:
            # Simulate a GET request to display all available products for sale
            response = client.get('/sales/display')
            print("Display Available Products Response:", response.get_json())

            # Simulate a GET request to retrieve product details
            response = client.get('/sales/product/some_product_id')  # Replace with a valid product_id
            print("Get Product Details Response:", response.get_json())

            # Simulate a POST request to purchase a product
            response = client.post('/sales/purchase', json={
                "username": "johndoe",  # Replace with a valid username
                "product_id": "some_product_id",  # Replace with a valid product_id
                "quantity": 1
            })
            print("Purchase Product Response:", response.get_json())

            # Simulate a GET request to retrieve purchase history for a customer
            response = client.get('/sales/history/johndoe')  # Replace with a valid username
            print("Get Purchase History Response:", response.get_json())

    pr.disable()  # Stop profiling

    # Save profiling results to a string
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s)
    ps.strip_dirs().sort_stats('cumulative').print_stats(10)  # Print top 10 functions by cumulative time

    # Print profiling results
    print(s.getvalue())

if __name__ == '__main__':
    run_profiling()