"""
This module initializes the SQLAlchemy instance used throughout the Flask app.

The `db` object is used to interact with the database and is configured for use with 
Flask models. This instance is passed to the app to connect the database to the 
Flask application.

Usage:
    The `db` instance can be used in other modules to define models, interact with 
    the database, and perform queries.
"""
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy instance
db = SQLAlchemy()
