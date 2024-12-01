Sales API Documentation
=======================

This section describes the API endpoints for managing sales transactions in the e-commerce system.

Available Goods for Sale
------------------------

.. http:get:: /sales/display

   Displays a list of available products with stock greater than zero.

   **Returns:**
   - A JSON list of products, each containing its `name` and `price`.

Product Details
---------------

.. http:get:: /sales/product/<product_id>

   Retrieves the details of a specific product by its ID.

   **Returns:**
   - A JSON object containing the product details, or an error message if the product is not found.

Purchase Product
----------------

.. http:post:: /sales/purchase

   Processes a product purchase by a customer.

   **Expected JSON data:**
   - `username` (str): The customer's username.
   - `product_id` (str): The ID of the product to purchase.
   - `quantity` (int): The quantity of the product to purchase.

   **Returns:**
   - A success message with product details and updated wallet balance if successful.
   - An error message if the transaction cannot be completed (e.g., insufficient stock or funds).

Customer Purchase History
-------------------------

.. http:get:: /sales/history/<username>

   Retrieves the purchase history for a specific customer.

   **Returns:**
   - A JSON object with the customer's information, or an error message if the customer is not found.
