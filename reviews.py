"""
Flask Application for Managing Reviews
--------------------------------------

This Flask app provides API endpoints for managing reviews on products in an e-commerce system.
The app interacts with two other services:
- **Customer Service**: Manages customer details.
- **Inventory Service**: Manages product details.

This service allows customers to submit, update, delete, and moderate reviews, as well as view reviews for products and customers.

The app uses SQLAlchemy for database interactions with a shared SQLite database.

Routes:
    - POST /reviews/submit: Submit a new review for a product.
    - PUT /reviews/update/<review_id>: Update an existing review.
    - DELETE /reviews/delete/<review_id>: Delete a review.
    - GET /reviews/product/<product_id>: Get all reviews for a specific product.
    - GET /reviews/customer/<username>: Get all reviews submitted by a specific customer.
    - POST /reviews/moderate/<review_id>: Moderate a review (flag as moderated).
    - GET /reviews/details/<review_id>: Get details for a specific review, including product and customer info.
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from customer import Customer, require_role, log_api_call  # Importing from previous services
from inventory import Product
from db_config import db 
from memory_profiler import profile
from bleach import clean
from sqlalchemy.exc import IntegrityError
from functools import wraps
from werkzeug.security import check_password_hash
import uuid

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'  # Shared database for all services
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # Initialize db with the app

# Authorization decorator to check if the user is the owner of the review
def authorize_review_owner(f):
    @wraps(f)
    def decorated_function(customer, *args, **kwargs):
        review_id = kwargs['review_id']
        review = Review.query.filter_by(review_id=review_id).first()
        if not review or review.customer_id != customer.customer_id:
            return jsonify({"error": "Unauthorized access to this review"}), 403
        return f(*args, **kwargs)
    return decorated_function

class Review(db.Model):
    """
    Review Model for E-commerce System
    -----------------------------------
    This model represents a review submitted by a customer for a product in the e-commerce system.

    Attributes:
        review_id (str): Unique identifier for the review.
        product_id (str): Foreign key linking to the Product being reviewed.
        customer_id (str): Foreign key linking to the Customer who submitted the review.
        rating (int): Rating given to the product (e.g., 1-5 stars).
        comment (str): Optional comment accompanying the review.
        moderated (bool): Flag indicating whether the review has been moderated.

    Relationships:
        product (Product): The product associated with this review.
        customer (Customer): The customer who submitted this review.

    Methods:
        to_dict: Converts the review object to a dictionary for easy JSON response.
    """

    __tablename__ = 'reviews'

    review_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = db.Column(db.String(36), db.ForeignKey('products.product_id'), nullable=False)
    customer_id = db.Column(db.String(36), db.ForeignKey('customers.customer_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(500), nullable=True)
    moderated = db.Column(db.Boolean, default=False)  # Flag to check if review is moderated

    # Define relationships
    product = db.relationship('Product', backref='reviews', lazy=True)
    customer = db.relationship('Customer', backref='reviews', lazy=True)

    def __init__(self, product_id, customer_id, rating, comment):
        self.product_id = product_id
        self.customer_id = customer_id
        self.rating = rating
        self.comment = comment

    def to_dict(self):
        return {
            'review_id': self.review_id,
            'product_id': self.product_id,
            'customer_id': self.customer_id,
            'rating': self.rating,
            'comment': self.comment,
            'moderated': self.moderated
        }

# Initialize the database (run this once to create the table)
with app.app_context():
    db.create_all()

# Authentication decorator
def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return jsonify({"error": "Basic auth required"}), 401
        
        customer = Customer.query.filter_by(username=auth.username).first()
        if not customer or not check_password_hash(customer.password, auth.password):
            return jsonify({"error": "Invalid credentials"}), 403
        
        return f(customer, *args, **kwargs)
    return decorated_function

# Authorization decorator to check if the user is the owner of the review
def authorize_review_owner(f):
    @wraps(f)
    def decorated_function(customer, *args, **kwargs):
        review_id = kwargs['review_id']
        review = Review.query.filter_by(review_id=review_id).first()
        if not review or review.customer_id != customer.customer_id:
            return jsonify({"error": "Unauthorized access to this review"}), 403
        return f(*args, **kwargs)
    return decorated_function

# Route for submitting a review
@app.route('/reviews/submit', methods=['POST'])
@profile
@authenticate
@log_api_call
def submit_review(customer):
    """
    Submit a review for a product.

    This route accepts a POST request to submit a review for a product. It requires the customer's username, 
    the product's ID, a rating, and an optional comment. It creates a new review in the database.

    Expected JSON data:
        - username (str): The username of the customer submitting the review.
        - product_id (str): The ID of the product being reviewed.
        - rating (int): The rating (e.g., 1-5 stars).
        - comment (str, optional): An optional comment about the product.

    Returns:
        Response: A success message with review details if the review is successfully submitted, 
                  or an error message if validation fails.
    """

    data = request.get_json()

    # Data validation
    if 'username' not in data or 'product_id' not in data or 'rating' not in data:
        return jsonify({"error": "Missing required fields"}), 400
    if not isinstance(data['rating'], int) or not (1 <= data['rating'] <= 5):
        return jsonify({"error": "Invalid rating. Must be an integer from 1 to 5."}), 400
    if data.get('comment') and not isinstance(data['comment'], str):
        return jsonify({"error": "Invalid comment. Must be a string."}), 400
    
    # Data sanitization
    comment = clean(data.get('comment', ""), tags=[], attributes={}, strip=True)

    # Get customer and product details
    customer = Customer.query.filter_by(username=data["username"]).first()
    product = Product.query.filter_by(product_id=data["product_id"]).first()

    if not customer:
        return jsonify({"message": "Customer not found."}), 404
    if not product:
        return jsonify({"message": "Product not found."}), 404

    # Create a new review
    new_review = Review(
        product_id=data["product_id"],
        customer_id=customer.customer_id,
        rating=data["rating"],
        comment=comment
    )

    db.session.add(new_review)
    db.session.commit()

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to submit review"}), 500

    return jsonify({"message": "Review submitted successfully", "review": new_review.to_dict()}), 201

# Route for updating a review
@app.route('/reviews/update/<string:review_id>', methods=['PUT'])
@profile
@authenticate
@authorize_review_owner
@log_api_call
def update_review(review_id):
    """
    Update an existing review.

    This route accepts a PUT request to update an existing review's rating or comment.

    Expected JSON data:
        - rating (int): The new rating (e.g., 1-5 stars).
        - comment (str): The updated comment.

    Args:
        review_id (str): The ID of the review to update.

    Returns:
        Response: A success message with the updated review details, or an error message if the review is not found.
    """

    review = Review.query.filter_by(review_id=review_id).first()
    if not review:
        return jsonify({"message": "Review not found."}), 404

    data = request.get_json()

    # Update review fields
    if "rating" in data:
         if not isinstance(data['rating'], int) or not (1 <= data['rating'] <= 5):
            return jsonify({"error": "Invalid rating. Must be an integer from 1 to 5."}), 400
         review.rating = data['rating']
    if "comment" in data:
        if not isinstance(data['comment'], str):
            return jsonify({"error": "Invalid comment. Must be a string."}), 400
        # Sanitize comment to prevent XSS
        sanitized_comment = clean(data['comment'], tags=[], attributes={}, strip=True)
        review.comment = sanitized_comment

    db.session.commit()

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Failed to update review."}), 500

    return jsonify({"message": "Review updated successfully", "review": review.to_dict()})


# Route for deleting a review
@app.route('/reviews/delete/<string:review_id>', methods=['DELETE'])
@profile
@authenticate
@authorize_review_owner
@log_api_call
def delete_review(review_id):
    """
    Delete a review by its ID.

    This route accepts a DELETE request to remove a review from the database.

    Args:
        review_id (str): The ID of the review to delete.

    Returns:
        Response: A success message if the review is deleted, or an error message if the review is not found.
    """

    review = Review.query.filter_by(review_id=review_id).first()
    if not review:
        return jsonify({"message": "Review not found."}), 404

    db.session.delete(review)
    db.session.commit()

    return jsonify({"message": "Review deleted successfully"})

# Route for getting all reviews for a product
@app.route('/reviews/product/<string:product_id>', methods=['GET'])
@profile
@log_api_call
def get_product_reviews(product_id):
    """
    Get all reviews for a specific product.

    This route accepts a GET request and returns all reviews for the specified product.

    Args:
        product_id (str): The ID of the product to retrieve reviews for.

    Returns:
        Response: A JSON list of reviews for the product, or an empty list if no reviews are found.
    """
    reviews = Review.query.filter_by(product_id=product_id).all()
    return jsonify([review.to_dict() for review in reviews])

# Route for getting all reviews submitted by a customer
@app.route('/reviews/customer/<string:username>', methods=['GET'])
@profile
@log_api_call
def get_customer_reviews(username):
    """
    Get all reviews submitted by a specific customer.

    This route accepts a GET request and returns all reviews submitted by the specified customer.

    Args:
        username (str): The username of the customer whose reviews are to be retrieved.

    Returns:
        Response: A JSON list of reviews submitted by the customer, or an error message if the customer is not found.
    """
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"message": "Customer not found."}), 404

    reviews = Review.query.filter_by(customer_id=customer.customer_id).all()
    return jsonify([review.to_dict() for review in reviews])

# Route for moderating a review (flag as moderated)
@app.route('/reviews/moderate/<string:review_id>', methods=['POST'])
@profile
@require_role('admin')
@log_api_call
def moderate_review(customer,review_id):
    """
    Moderate a review (flag as moderated).

    This route accepts a POST request to flag a review as moderated.

    Args:
        review_id (str): The ID of the review to moderate.

    Returns:
        Response: A success message if the review is moderated, or an error message if the review is not found.
    """
    review = Review.query.filter_by(review_id=review_id).first()
    if not review:
        return jsonify({"message": "Review not found."}), 404

    review.moderated = True
    db.session.commit()

    return jsonify({
        "message": "Review moderated successfully",
        "review": review.to_dict()
    })
@app.route('/reviews/details/<string:review_id>', methods=['GET'])
@profile
@log_api_call
def get_review_details(review_id):
    """
    Get detailed information about a specific review.

    This route accepts a GET request and returns detailed information about the specified review,
    including the reviewer's username and the product name.

    Args:
        review_id (str): The ID of the review to retrieve details for.

    Returns:
        Response: A JSON object with review details, or an error message if the review is not found.
    """
    # Fetch the review using the provided review_id
    review = Review.query.filter_by(review_id=review_id).first()
    
    # If the review doesn't exist, return a 404 error
    if not review:
        return jsonify({"message": "Review not found."}), 404

    # Fetch the customer and product using the customer_id and product_id from the review
    customer = Customer.query.filter_by(customer_id=review.customer_id).first()
    product = Product.query.filter_by(product_id=review.product_id).first()

    # If the customer or product is not found, return an error
    if not customer or not product:
        return jsonify({"message": "Customer or Product not found."}), 404

    # Return the review details along with the customer username and product name
    return jsonify({
        "review_id": review.review_id,
        "rating": review.rating,
        "comment": review.comment,
        "moderated": review.moderated,
        "customer_username": customer.username,  # Use customer.username instead of customer_id
        "product_name": product.name  # Use product.name instead of product_id
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)  # Service 4 running on port 5003
