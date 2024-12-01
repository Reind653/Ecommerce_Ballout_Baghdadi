import cProfile
import pstats
import io
from flask import Flask
from reviews import app  # Import your Flask app

def run_profiling():
    pr = cProfile.Profile()
    pr.enable()  # Start profiling

    # Simulate requests to the Flask app
    with app.test_request_context():
        with app.test_client() as client:
            # Simulate a POST request to submit a new review
            response = client.post('/reviews/submit', json={
                "username": "johndoe",  # Replace with a valid username
                "product_id": "some_product_id",  # Replace with a valid product_id
                "rating": 5,
                "comment": "Great product!"
            })
            print("Submit Review Response:", response.get_json())

            # Simulate a GET request to retrieve all reviews for a specific product
            response = client.get('/reviews/product/some_product_id')  # Replace with a valid product_id
            print("Get Product Reviews Response:", response.get_json())

            # Simulate a GET request to retrieve all reviews submitted by a specific customer
            response = client.get('/reviews/customer/johndoe')  # Replace with a valid username
            print("Get Customer Reviews Response:", response.get_json())

            # Simulate a PUT request to update a review
            response = client.put('/reviews/update/some_review_id', json={
                "rating": 4,
                "comment": "Updated comment."
            })  # Replace with a valid review_id
            print("Update Review Response:", response.get_json())

            # Simulate a DELETE request to delete a review
            response = client.delete('/reviews/delete/some_review_id')  # Replace with a valid review_id
            print("Delete Review Response:", response.get_json())

            # Simulate a POST request to moderate a review
            response = client.post('/reviews/moderate/some_review_id')  # Replace with a valid review_id
            print("Moderate Review Response:", response.get_json())

            # Simulate a GET request to get details for a specific review
            response = client.get('/reviews/details/some_review_id')  # Replace with a valid review_id
            print("Get Review Details Response:", response.get_json())

    pr.disable()  # Stop profiling

    # Save profiling results to a string
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s)
    ps.strip_dirs().sort_stats('cumulative').print_stats(10)  # Print top 10 functions by cumulative time

    # Print profiling results
    print(s.getvalue())

if __name__ == '__main__':
    run_profiling()