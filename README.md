
# E-commerce Backend API

### Project Overview

This project implements a backend for an e-commerce platform, consisting of four services: **Customers**, **Inventory**, **Sales**, and **Reviews**. These services communicate via API calls and are designed to manage customers, products, sales transactions, and product reviews. The system is built using **Flask** and **SQLAlchemy** for API services and data management, containerized using **Docker** for easy deployment and scalability.

### Project Purpose

The purpose of this project is to build an efficient and secure backend system for an e-commerce platform, where each service handles a different aspect of the business operations. The goal is to create a scalable and modular system that communicates between services using RESTful APIs, with robust features like user authentication, data validation, and moderation.

### Objectives

- **Create four services** for customer management, inventory, sales processing, and product reviews.
- **Develop RESTful APIs** for each service that allow seamless communication between the components.
- **Ensure security and data validation** by implementing features like user authentication and input sanitization.
- **Containerize the services** using Docker for consistent deployment across different environments.
- **Test the system thoroughly** with unit tests and integration tests.

### Technologies Used

- **Flask** – Python framework for building web APIs.
- **SQLAlchemy** – ORM used to interact with the database.
- **Docker** – Used for containerizing the services.
- **Postman** – For API testing and documentation.
- **Pytest** – For testing the APIs and ensuring the functionality of the services.
---

### Services Overview

#### 1. Customers Service

The Customers service handles user registration, wallet management, and user details. The following operations are supported:
- **Register**: Register new customers, ensuring unique usernames.
- **Update**: Update customer information (name, address, etc.).
- **Charge Wallet**: Add funds to the customer’s wallet.
- **Deduct Wallet**: Deduct funds from the customer’s wallet when making a purchase.
- **Delete**: Delete customer data from the system.

#### 2. Inventory Service

The Inventory service manages the products in the store. It provides APIs for:
- **Adding Products**: Add new products with details like price, category, and stock quantity.
- **Updating Products**: Modify product details (price, description, stock).
- **Removing Products**: Decrease stock or remove products from the inventory.

#### 3. Sales Service

The Sales service handles the purchasing process:
- **Display Available Goods**: Shows all available products for purchase.
- **Purchase**: Process a sale, deduct money from the customer's wallet, and update inventory stock.
- **Sales History**: Maintain records of purchases made by each customer.

#### 4. Reviews Service

The Reviews service enables customers to provide feedback on products:
- **Submit Review**: Allows customers to submit ratings and comments for products.
- **Update Review**: Modify an existing review.
- **Delete Review**: Remove a review.
- **Moderate Review**: Administrators can moderate reviews to ensure content quality.
- **Get Reviews**: Fetch all reviews for a specific product or customer.

---

### Setup and Installation

#### Prerequisites

- **Docker**: Make sure Docker is installed on your system. You can download Docker [here](https://www.docker.com/products/docker-desktop).
- **Python 3.x**: Ensure Python is installed on your local machine.

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/Ecommerce_Familyname.git
cd Ecommerce_Ballout_Baghdadi
```

#### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set Up Docker

To run the services and the database containerized:

1. Navigate to the project directory containing the `docker-compose.yml` file.
2. Build and start the containers:

```bash
docker-compose up --build
```

#### 5. Running the Application

The backend services will be accessible at the following ports:
- **Customers Service**: `http://localhost:5000`
- **Inventory Service**: `http://localhost:5001`
- **Sales Service**: `http://localhost:5002`
- **Reviews Service**: `http://localhost:5003`

You can test the APIs using **Postman** by importing the collection provided in the project.
---

### API Documentation

The APIs are documented using **Postman**. Each API is described with:
- **Endpoint**
- **Request Parameters**
- **Response Examples**
- **Error Codes**

To get started with Postman, import the collection from the following link:

https://api.postman.com/collections/38530826-81e055f0-f3ef-4257-87c6-fde093c1ac9f?access_key={add key}

---

### Testing

We’ve implemented unit and integration tests using **Pytest**. To run the tests:

```bash
pytest test_customer.py
pytest test_inventory.py
pytest test_sales.py
pytest test_reviews.py
```

This will run all the test cases and show the results.

---

### Performance Profiling

Performance profiling has been done using **cProfile** and **memory_profiler**.

---

### Security Measures

The application follows best practices for security, including:
- **End-to-end encryption** 
- **SQL Injection Protection** using **SQLAlchemy ORM**.
- **User Authentication** using basic auth and JWT for token-based sessions.
- **Role-Based Access Control (RBAC)** for restricting sensitive operations.


---

### Troubleshooting

- **Error: Unable to connect to the database**: Ensure Docker is running and the `docker-compose.yml` file is correctly configured.
- **Error: 403 Unauthorized**: Check if the correct authentication token or credentials are provided.

---

### References

1. Stallings, William. *Cryptography and Network Security: Principles and Practice*. 7th ed., Pearson, 2016.
2. Grinberg, Miguel. *Flask Web Development: Developing Web Applications with Python*. 2nd ed., O'Reilly Media, 2018.
3. Sandhu, Ravi, et al. "Role-Based Access Control Models." *IEEE Computer*, vol. 29, no. 2, 1996, pp. 38-47.

---

### License

This project is for EECE 435 L.

