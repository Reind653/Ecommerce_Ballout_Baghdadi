Flask Application Configuration
=============================

The Flask app uses **SQLAlchemy** for database interaction. The `db` instance is initialized 
with the `SQLAlchemy()` class and is used throughout the application to interact with the 
database models.

Initialization of SQLAlchemy instance:

.. code-block:: python

    from flask_sqlalchemy import SQLAlchemy

    # Initialize SQLAlchemy instance
    db = SQLAlchemy()

This `db` instance is passed to the app, allowing the app to interact with the database 
through defined models.

Usage:
------
Once initialized, the `db` instance is used in other modules to define models, perform queries, 
and manage database interactions. For example:

.. code-block:: python

    from config import db
    from models import Product

    # Example of creating a new product
    new_product = Product(name="Example", category="Electronics", price=99.99, stock_count=100)
    db.session.add(new_product)
    db.session.commit()
