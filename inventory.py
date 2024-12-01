"""
Flask Application for Managing Product Inventory
------------------------------------------------
This Flask application provides an API for managing the product inventory in an e-commerce system.
It includes routes for adding, updating, removing, and fetching products.

The app uses SQLAlchemy for database interactions and stores product data in an SQLite database.

Routes:
    - POST /inventory/add: Adds a new product to the inventory.
    - PUT /inventory/<product_id>/update: Updates the details of an existing product.
    - POST /inventory/<product_id>/deduct: Deducts stock from a product's inventory.
    - GET /inventory: Retrieves all products in the inventory.
    - GET /inventory/<name>: Retrieves a specific product by name.
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from db_config import db 
from memory_profiler import profile
from customer import Customer,require_role, log_api_call
import uuid

# Initialize Flask app
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'  # Shared database for all services
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize db with the app
# Product model for Inventory
class Product(db.Model):
    """
    Product Model for E-commerce Inventory
    --------------------------------------
    This model represents a product in the e-commerce system's inventory. It stores product details like 
    name, category, price, description, and stock count.

    Attributes:
        product_id (str): Unique identifier for the product.
        name (str): Name of the product.
        category (str): Category of the product (e.g., 'food', 'clothes').
        price (float): Price of the product.
        description (str): Description of the product (optional).
        stock_count (int): Number of items available in stock.
    Methods:
        to_dict: Converts the product object to a dictionary for easy JSON response.
    """
    __tablename__ = 'products'

    product_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., 'food', 'clothes', etc.
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    stock_count = db.Column(db.Integer, default=0, nullable=False)

    def __init__(self, name, category, price, description, stock_count):
        self.name = name
        self.category = category
        self.price = price
        self.description = description
        self.stock_count = stock_count

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category,
            'price': self.price,
            'description': self.description,
            'stock_count': self.stock_count
        }

# Initialize the database (run this once to create the table)
with app.app_context():
    db.create_all()

# Route for adding goods to the inventory
@app.route('/inventory/add', methods=['POST'])
@profile
@require_role('admin')
@log_api_call
def add_goods(customer):
    """
    Adds a new product to the inventory.

    This route accepts a POST request with product data in JSON format and adds a new product to the inventory.

    Expected JSON data:
        - name (str): Name of the product.
        - category (str): Category of the product (e.g., 'food', 'clothes').
        - price (float): Price of the product.
        - description (str): Description of the product (optional).
        - stock_count (int): Number of items available in stock.

    Returns:
        Response: JSON response with a success message and product details, or an error message if validation fails.
    """
    data = request.get_json()

    # Validate required fields
    required_fields = ["name", "category", "price", "stock_count"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"{field} is required."}), 400

    # Create a new product
    new_product = Product(
        name=data["name"],
        category=data["category"],
        price=data["price"],
        description=data.get("description"),
        stock_count=data["stock_count"]
    )

    db.session.add(new_product)
    db.session.commit()

    return jsonify({
        "message": "Product added successfully",
        "product": new_product.to_dict()
    }), 201

# Route for updating a product's details
@app.route('/inventory/<string:product_id>/update', methods=['PUT'])
@profile
@log_api_call
@require_role('admin')
def update_goods(customer,product_id):
    """
    Updates a product's details.

    This route accepts a PUT request to update the details of a specific product identified by its product_id.

    Expected JSON data (optional fields):
        - name (str): Name of the product.
        - category (str): Category of the product.
        - price (float): Price of the product.
        - description (str): Description of the product.
        - stock_count (int): Number of items available in stock.

    Args:
        product_id (str): The unique identifier of the product to update.

    Returns:
        Response: JSON response with a success message and updated product details, or an error message if product is not found.
    """
    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return jsonify({"message": "Product not found."}), 404

    data = request.get_json()

    # Update fields that are provided in the request
    if "name" in data:
        product.name = data["name"]
    if "category" in data:
        product.category = data["category"]
    if "price" in data:
        product.price = data["price"]
    if "description" in data:
        product.description = data["description"]
    if "stock_count" in data:
        product.stock_count = data["stock_count"]

    db.session.commit()

    return jsonify({
        "message": "Product information updated successfully",
        "product": product.to_dict()
    })

# Route for removing products from stock
@app.route('/inventory/<string:product_id>/deduct', methods=['POST'])
@profile
@log_api_call
@require_role('admin')
def deduct_goods(customer,product_id):
    """
    Deducts stock from a product's inventory.

    This route accepts a POST request to deduct a specified quantity from the stock count of a product.

    Expected JSON data:
        - quantity (int): The quantity of the product to deduct from the stock.

    Args:
        product_id (str): The unique identifier of the product to update.

    Returns:
        Response: JSON response with a success message and the updated product details, or an error message if product is not found or insufficient stock.
    """

    product = Product.query.filter_by(product_id=product_id).first()
    if not product:
        return jsonify({"message": "Product not found."}), 404

    data = request.get_json()
    quantity_to_deduct = data.get("quantity", 0)

    if quantity_to_deduct <= 0:
        return jsonify({"message": "Quantity to deduct must be greater than zero."}), 400

    if product.stock_count < quantity_to_deduct:
        return jsonify({"message": "Not enough stock available."}), 400

    product.stock_count -= quantity_to_deduct
    db.session.commit()

    return jsonify({
        "message": f"{quantity_to_deduct} items deducted successfully.",
        "product": product.to_dict()
    })

# Route for getting all products in the inventory
@app.route('/inventory', methods=['GET'])
@profile
@log_api_call
def get_all_goods():
    """
    Retrieves all products in the inventory.

    This route accepts a GET request and returns a list of all products in the inventory.

    Returns:
        Response: JSON response containing a list of all products, or an empty list if no products exist.
    """
    products = Product.query.all()
    return jsonify([product.to_dict() for product in products])

# Route for getting a specific product by its name
@app.route('/inventory/<string:name>', methods=['GET'])
@profile
@log_api_call
def get_product_by_name(name):
    """
    Retrieves a specific product by its name.

    This route accepts a GET request and returns the details of the product with the specified name.

    Args:
        name (str): The name of the product to retrieve.

    Returns:
        Response: JSON response containing the product details, or an error message if the product is not found.
    """
    product = Product.query.filter_by(name=name).first()
    if not product:
        return jsonify({"message": "Product not found."}), 404
    return jsonify(product.to_dict())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
