"""
Flask Application for Managing Sales
------------------------------------

This Flask app provides API endpoints for handling sales transactions in an e-commerce system. 
The app interacts with two other services:
- **Customer Service**: Manages customer details.
- **Inventory Service**: Manages products and their stock.

The app uses SQLAlchemy for database interactions with a shared SQLite database.

Routes:
    - GET /sales/display: Displays all available products for sale.
    - GET /sales/product/<product_id>: Retrieves detailed information about a product.
    - POST /sales/purchase: Processes a product purchase by a customer.
    - GET /sales/history/<username>: Retrieves the purchase history for a specific customer.
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from customer import Customer , log_api_call # Importing Customer model from Service 1
from inventory import Product
from memory_profiler import profile
from db_config import db 

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'  # Shared database for all services
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)  # Initialize db with the app

# Route for displaying all available goods for sale
@app.route('/sales/display', methods=['GET'])
@profile
@log_api_call
def display_available_goods():
    """
    Displays all available products for sale with stock greater than zero.

    This route accepts a GET request and returns a list of products that have a positive stock count 
    and are available for sale.

    Returns:
        Response: A JSON list of products, each containing its `name` and `price`.
    """
    products = Product.query.filter(Product.stock_count > 0).all()  # Check for products with stock
    #return jsonify([product.to_dict() for product in products])
    return jsonify([{'name': product.name, 'price': product.price} for product in products])

# Route for getting product details
@app.route('/sales/product/<string:product_id>', methods=['GET'])
@profile
@log_api_call
def get_product_details(product_id):
    """
    Retrieves the details of a specific product by its ID.

    This route accepts a GET request and returns detailed information about the product specified by 
    its `product_id`.

    Args:
        product_id (str): The ID of the product to retrieve.

    Returns:
        Response: A JSON object with product details if found, or an error message if not found.
    """
    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return jsonify({"message": "Product not found."}), 404
    return jsonify(product.to_dict())

# Route for processing a sale (purchase by customer)
@app.route('/sales/purchase', methods=['POST'])
@profile
@log_api_call
def purchase_product():
    """
    Processes a product purchase by a customer.

    This route accepts a POST request with the customer's username, the product's ID, and the quantity 
    they wish to purchase. It checks the availability of stock, verifies the customer's funds, and 
    processes the transaction by deducting money from the customer's wallet and updating the product's stock.

    Expected JSON data:
        - username (str): The customer's username.
        - product_id (str): The ID of the product to purchase.
        - quantity (int): The quantity of the product to purchase.

    Returns:
        Response: A success message with product details and updated wallet balance if the transaction is successful, 
        or an error message if validation fails.
    """
    data = request.get_json()

    # Validate required fields
    required_fields = ["username", "product_id", "quantity"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"{field} is required."}), 400

    # Get customer and product details
    customer = Customer.query.filter_by(username=data["username"]).first()
    product = Product.query.filter_by(product_id=data["product_id"]).first()

    if not customer:
        return jsonify({"message": "Customer not found."}), 404
    if not product:
        return jsonify({"message": "Product not found."}), 404

    quantity = data["quantity"]

    # Check if there is enough stock
    if product.stock_count < quantity:
        return jsonify({"message": "Not enough stock available."}), 400

    # Check if the customer has enough money
    total_price = product.price * quantity
    if customer.wallet_balance < total_price:
        return jsonify({"message": "Insufficient funds."}), 400

    # Deduct money from customer wallet and update stock count
    customer.wallet_balance -= total_price
    product.stock_count -= quantity

    # Save the changes to the database
    db.session.commit()

    return jsonify({
        "message": "Purchase successful",
        "product": product.to_dict(),
        "customer_wallet_balance": customer.wallet_balance
    })

# Route for getting the purchase history of a customer
@app.route('/sales/history/<string:username>', methods=['GET'])
@profile
@log_api_call
def get_purchase_history(username):
    """
    Retrieves the purchase history for a specific customer.

    This route accepts a GET request and returns the customer's purchase history, based on their `username`. 
    In this simple example, the history is represented by the customer's details, but more complex logic could 
    be added to track individual purchases.

    Args:
        username (str): The username of the customer whose purchase history is being retrieved.

    Returns:
        Response: A JSON object with the customer's information, or an error message if the customer is not found.
    """
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"message": "Customer not found."}), 404

    # In this simple example, we are just showing customer information; you can add logic to store purchases separately.
    return jsonify({
        "message": f"Showing purchase history for {username}",
        "customer": customer.to_dict()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)  # Service 3 running on port 5001
