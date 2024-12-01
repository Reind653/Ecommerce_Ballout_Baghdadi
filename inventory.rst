Product API Documentation
=========================

This section describes the API endpoints for managing products in the inventory system.

Product Model
-------------

The `Product` model represents a product in the inventory system. It includes attributes like `name`, `category`, `price`, `description`, and `stock_count`.

.. autoclass:: Product
   :members:
   :undoc-members:
   :show-inheritance:

API Endpoints
-------------

### Add Product to Inventory

.. http:post:: /inventory/add

   Adds a new product to the inventory.

   **Expected JSON data:**
   
   - `name` (str): Name of the product.
   - `category` (str): Category of the product (e.g., 'food', 'clothes').
   - `price` (float): Price of the product.
   - `description` (str, optional): Description of the product.
   - `stock_count` (int): Number of items available in stock.

   **Returns:**
   - A success message with product details if the product is added.
   - Error message if any required field is missing or invalid.

### Update Product Details

.. http:put:: /inventory/<product_id>/update

   Updates the details of an existing product.

   **Expected JSON data:**
   
   - `name` (str): Name of the product (optional).
   - `category` (str): Category of the product (optional).
   - `price` (float): Price of the product (optional).
   - `description` (str): Description of the product (optional).
   - `stock_count` (int): Number of items available in stock (optional).

   **Returns:**
   - A success message with updated product details.
   - Error message if the product is not found.

### Deduct Stock from Product

.. http:post:: /inventory/<product_id>/deduct

   Deducts stock from a product's inventory.

   **Expected JSON data:**
   
   - `quantity` (int): Number of items to deduct from stock.

   **Returns:**
   - A success message with the updated stock count.
   - Error message if the quantity is invalid or insufficient stock is available.

### Get All Products

.. http:get:: /inventory

   Retrieves a list of all products in the inventory.

   **Returns:**
   - A JSON array containing all products, or an empty array if no products exist.

### Get Product by Name

.. http:get:: /inventory/<name>

   Retrieves a specific product by its name.

   **Returns:**
   - A JSON object containing the product details, or an error message if the product is not found.
