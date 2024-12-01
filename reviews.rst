Reviews API Documentation
=========================

This section describes the API endpoints for managing product reviews.

Review Model
-------------

The `Review` model represents a product review submitted by a customer. Each review is associated 
with a product and a customer.

Attributes:
    - `review_id` (str): Unique identifier for the review.
    - `product_id` (str): Foreign key linking to the Product being reviewed.
    - `customer_id` (str): Foreign key linking to the Customer who submitted the review.
    - `rating` (int): Rating given to the product (1-5 stars).
    - `comment` (str): Optional comment accompanying the review.
    - `moderated` (bool): Flag indicating whether the review has been moderated.

Methods:
    - `to_dict`: Converts the review object to a dictionary format for easy JSON response.

API Endpoints
-------------

### Submit Review

.. http:post:: /reviews/submit

   Submits a review for a product.

   **Expected JSON data:**
   - `username` (str): The customer's username.
   - `product_id` (str): The ID of the product being reviewed.
   - `rating` (int): The rating (1-5 stars).
   - `comment` (str, optional): An optional comment.

   **Returns:**
   - A success message with review details if the review is successfully submitted, 
     or an error message if validation fails.

### Update Review

.. http:put:: /reviews/update/<review_id>

   Updates an existing review's rating or comment.

   **Expected JSON data:**
   - `rating` (int): The updated rating (1-5 stars).
   - `comment` (str): The updated comment.

   **Returns:**
   - A success message with updated review details, or an error message if the review is not found.

### Delete Review

.. http:delete:: /reviews/delete/<review_id>

   Deletes a review by its ID.

   **Returns:**
   - A success message if the review is deleted, or an error message if the review is not found.

### Get Product Reviews

.. http:get:: /reviews/product/<product_id>

   Retrieves all reviews for a specific product.

   **Returns:**
