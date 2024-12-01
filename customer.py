"""
Flask Application for Managing Customer Accounts
-------------------------------------------------
This Flask application provides an API for managing customer accounts in an e-commerce system.
It includes routes for customer registration, deletion, updating information, viewing customers,
charging and deducting from wallets, and more.

The app uses SQLAlchemy for database interactions and stores customer data in an SQLite database.

Routes:
    - POST /customers/register: Registers a new customer.
    - DELETE /customers/<username>/delete: Deletes a customer by username.
    - PUT /customers/<username>/update: Updates customer information.
    - GET /customers: Retrieves all customers.
    - GET /customers/<username>: Retrieves a customer by username.
    - POST /customers/<username>/charge: Charges a customer's wallet.
    - POST /customers/<username>/deduct: Deducts money from a customer's wallet.
"""

from flask import Flask, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from db_config import db  # Import shared db object
from memory_profiler import profile
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from cryptography.fernet import Fernet
import os
import logging
from logging.handlers import RotatingFileHandler

# Initialize the Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'  # Shared database for all services
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db.init_app(app)  # Initialize db with the app
# Customer model
key = "UurdlpZp2i1fT0B7ANozGlq5NBVRsHgt1YhpHa4RGEE="
cipher = Fernet(key)

def encrypt(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()

def decrypt(data: str) -> str:
    return cipher.decrypt(data.encode()).decode()

# Setup logger
def setup_logger():
    handler = RotatingFileHandler('api_logs.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

setup_logger()

def log_api_call(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log request details safely
        data = request.get_json(silent=True, cache=True)
        app.logger.info(f'Request - Path: {request.path}, Method: {request.method}, Body: {data}')

        # Execute the actual function and get the response
        response = f(*args, **kwargs)

        # Check the type of response and handle logging appropriately
        if isinstance(response, Response):
            # Assuming you want to log JSON data if possible
            try:
                response_data = response.get_json()
                app.logger.info(f'Response - Status: {response.status_code}, Body: {response_data}')
            except Exception as e:
                # If response is not JSON serializable, log the exception or handle differently
                app.logger.error(f'Error getting JSON from response: {e}')
        elif isinstance(response, tuple):
            # Handle tuples, usually (response_body, status)
            response_body, status_code = response
            app.logger.info(f'Response - Status: {status_code}, Body: {response_body}')
        else:
            # If response is a simple data structure or a direct value
            app.logger.info(f'Response - Status: {response.status_code}, Body: {response.data}')

        return response

    return decorated_function


class Customer(db.Model):
    """
    Customer Model for E-commerce System
    ------------------------------------
    This model represents a customer in the e-commerce system. It stores basic customer information
    like name, username, password (hashed in production), age, address, gender, marital status, and wallet balance.

    Attributes:
        customer_id (str): Unique identifier for the customer.
        fullname (str): Full name of the customer.
        username (str): Unique username of the customer.
        password (str): Password of the customer (should be hashed in production).
        age (int): Age of the customer.
        address (str): Address of the customer.
        gender (str): Gender of the customer.
        marital_status (str): Marital status of the customer.
        wallet_balance (float): Wallet balance of the customer (default is 0.0).

    Methods:
        to_dict: Converts the customer object to a dictionary for easy JSON response.
    """
    __tablename__ = 'customers'
    
    customer_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # In production, use hashed passwords
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    marital_status = db.Column(db.String(20), nullable=False)
    wallet_balance = db.Column(db.Float, default=0.0)
    role = db.Column(db.String(20), default="user")  # Default role as 'user'

    def __init__(self, fullname, username, password, age, address, gender, marital_status, role="user"):
        self.fullname = fullname
        self.username = username
        self.password = password
        self.age = age
        self.address = address
        self.gender = gender
        self.marital_status = marital_status
        self.role = role

    def has_role(self, role_name):
        return self.role == role_name
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    # Convert the object to a dictionary format for easy JSON response
    def to_dict(self):
        """
    Converts the customer object to a dictionary format.

    Returns:
        dict: A dictionary containing the customer information.
    """
        return {
            'customer_id': self.customer_id,
            'fullname': self.fullname,
            'username': self.username,
            'age': self.age,
            'address': self.address,
            'gender': self.gender,
            'marital_status': self.marital_status,
            'wallet_balance': self.wallet_balance,
            'role': self.role
        }

# Initialize the database (run this once to create the table)
with app.app_context():
    db.create_all()

def require_role(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth = request.authorization
            if not auth:
                return jsonify({"error": "Authentication required"}), 401
            
            customer = Customer.query.filter_by(username=auth.username).first()
            if not customer:
                return jsonify({"error": "User not found"}), 404

            if not customer.has_role(required_role):
                return jsonify({"error": "Insufficient permissions"}), 403
            
            return f(customer, *args, **kwargs)
        return decorated_function
    return decorator

# Route for registering a new customer
@app.route('/customers/register', methods=['POST'])
@profile
@log_api_call
def register_customer():
    """
    Registers a new customer in the system.

    This route accepts a POST request with customer data in JSON format and creates a new customer in the database.

    Expected JSON data:
        - fullname (str): Full name of the customer.
        - username (str): Unique username of the customer.
        - password (str): Password of the customer (should be hashed in production).
        - age (int): Age of the customer.
        - address (str): Address of the customer.
        - gender (str): Gender of the customer.
        - marital_status (str): Marital status of the customer.

    Returns:
        Response: JSON response with a success message and customer details, or error message if validation fails.
    """
    data = request.get_json()

    # Validate required fields
    required_fields = ["fullname", "username", "password", "age", "address", "gender", "marital_status"]
    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"{field} is required."}), 400

    # Check if username is unique
    if Customer.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "Username already taken."}), 400

    role = data.get('role', 'user')
    encrypted_fullname = encrypt(data["fullname"])
    encrypted_address = encrypt(data["address"])
    # Create a new customer and add to the database
    new_customer = Customer(
        fullname=encrypted_fullname,
        username=data["username"],
        password=generate_password_hash(data['password']),
        age=data["age"],
        address=encrypted_address,
        gender=data["gender"],
        marital_status=data["marital_status"],
        role=role
    )

    db.session.add(new_customer)
    db.session.commit()
    print("MY ROLE IS ",new_customer.role)
    return jsonify({
        "message": "Customer registered successfully",
        "customer": new_customer.to_dict()
    }), 201

# Route for deleting a customer by username
@app.route('/customers/<string:username>/delete', methods=['DELETE'])
@profile
@log_api_call
def delete_customer(username):
    """
    Deletes a customer by username.

    This route accepts a DELETE request and removes the customer with the specified username from the database.

    Args:
        username (str): The username of the customer to delete.

    Returns:
        Response: JSON response with a success or error message.
    """
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"message": "Customer not found."}), 404

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully"})

# Route for updating customer information
@app.route('/customers/<string:username>/update', methods=['PUT'])
@profile
@log_api_call
def update_customer(username):
    '''
    Updates an existing customer's information.

    This route accepts a PUT request to update the customer details for the specified username.
    Only the fields provided in the request will be updated.

    Expected JSON data (optional fields):
        - fullname (str): Full name of the customer.
        - age (int): Age of the customer.
        - address (str): Address of the customer.
        - gender (str): Gender of the customer.
        - marital_status (str): Marital status of the customer.
    Args:
        username (str): The username of the customer whose details are being updated.

    Returns:
        Response: JSON response with a success message and updated customer details, or error message if customer is not found.
    """
    '''
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"message": "Customer not found."}), 404

    data = request.get_json()
    encrypted_fullname = encrypt(data["fullname"])
    encrypted_address = encrypt(data["address"])

    # Update fields that are provided in the request
    if "fullname" in data:
        customer.fullname = encrypted_fullname
    if "age" in data:
        customer.age = data["age"]
    if "address" in data:
        customer.address = encrypted_address
    if "gender" in data:
        customer.gender = data["gender"]
    if "marital_status" in data:
        customer.marital_status = data["marital_status"]

    db.session.commit()

    return jsonify({
        "message": "Customer information updated successfully",
        "customer": customer.to_dict()
    })

# Route for getting all customers
@app.route('/customers', methods=['GET'])
@log_api_call
@profile

def get_all_customers():
    """
    Retrieves all customers in the system.

    This route accepts a GET request and returns a list of all customers in the database.

    Returns:
        Response: JSON response containing a list of all customers in the system, or an empty list if no customers exist.
    """
    customers = Customer.query.all()
    customer_list = []

    for customer in customers:
        # Decrypt sensitive data fields
        customer_data = {
            'customer_id': customer.customer_id,
            'fullname': decrypt(customer.fullname),
            'username': customer.username,
            'age': customer.age,
            'address': decrypt(customer.address),
            'gender': customer.gender,
            'marital_status': customer.marital_status,
            'wallet_balance': customer.wallet_balance,
            'role': customer.role
        }
        customer_list.append(customer_data)

    return jsonify(customer_list)

# Route for getting a specific customer by username
@app.route('/customers/<string:username>', methods=['GET'])
@profile
@log_api_call
def get_customer_by_username(username):
    """
    Retrieves a customer by their username.

    This route accepts a GET request and returns the details of a customer based on the provided username.

    Args:
        username (str): The username of the customer to retrieve.

    Returns:
        Response: JSON response containing the customer details, or an error message if the customer is not found.
    """
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"message": "Customer not found."}), 404

    customer_data = {
        'fullname': decrypt(customer.fullname),
        'username': customer.username,
        'age': customer.age,
        'address': decrypt(customer.address),
        'gender': customer.gender,
        'marital_status': customer.marital_status,
        'wallet_balance': customer.wallet_balance
    }
    return jsonify(customer_data)

# Route for charging a customer's wallet
@app.route('/customers/<string:username>/charge', methods=['POST'])
@profile
@log_api_call
def charge_customer_wallet(username):
    """
    Charges a customer's wallet by adding a specified amount.

    This route accepts a POST request to charge the wallet of a customer with a specified amount.

    Expected JSON data:
        - amount (float): The amount to add to the customer's wallet.

    Args:
        username (str): The username of the customer whose wallet is being charged.

    Returns:
        Response: JSON response with success or error message, and the updated wallet balance.
    """
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"message": "Customer not found."}), 404

    data = request.get_json()
    amount = data.get("amount")
    if not amount or amount <= 0:
        return jsonify({"message": "Amount must be greater than zero."}), 400

    customer.wallet_balance += amount
    db.session.commit()

    return jsonify({
        "message": "Account charged successfully",
        "wallet_balance": customer.wallet_balance
    })

# Route for deducting money from customer's wallet
@app.route('/customers/<string:username>/deduct', methods=['POST'])
@profile
@log_api_call
def deduct_from_wallet(username):
    customer = Customer.query.filter_by(username=username).first()
    if not customer:
        return jsonify({"message": "Customer not found."}), 404

    data = request.get_json()
    amount = data.get("amount")
    if not amount or amount <= 0:
        return jsonify({"message": "Amount must be greater than zero."}), 400

    if customer.wallet_balance < amount:
        return jsonify({"message": "Insufficient balance."}), 400

    customer.wallet_balance -= amount
    db.session.commit()

    return jsonify({
        "message": "Amount deducted successfully",
        "wallet_balance": customer.wallet_balance
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
