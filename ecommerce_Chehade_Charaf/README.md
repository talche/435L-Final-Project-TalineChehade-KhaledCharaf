
# E-commerce Backend Project

An e-commerce backend application built using microservices architecture with Flask and MySQL. The project consists of four main services:

- **Customers Service**: Manages customer registration, authentication, and profile management.
- **Inventory Service**: Handles goods management, including adding, updating, and deleting products.
- **Sales Service**: Manages sales transactions, purchase processing, and purchase history.
- **Reviews Service**: Handles product reviews and ratings, including moderation features.

All services are containerized using Docker and orchestrated with Docker Compose for easy deployment and management.

---

## Table of Contents

- [E-commerce Backend Project](#e-commerce-backend-project)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Project Overview](#project-overview)
  - [Features](#features)
  - [Architecture](#architecture)
  - [Technologies Used](#technologies-used)
  - [Microservices](#microservices)
    - [Customers Service](#customers-service)
    - [Inventory Service](#inventory-service)
    - [Sales Service](#sales-service)
    - [Reviews Service](#reviews-service)
  - [Installation and Setup](#installation-and-setup)
    - [Prerequisites](#prerequisites)
    - [Clone the Repository](#clone-the-repository)
    - [Environment Variables](#environment-variables)
    - [Building and Running with Docker Compose](#building-and-running-with-docker-compose)
  - [Usage](#usage)
    - [Accessing the Services](#accessing-the-services)
    - [API Endpoints](#api-endpoints)
      - [Customers Service Endpoints](#customers-service-endpoints)
      - [Inventory Service Endpoints](#inventory-service-endpoints)
      - [Sales Service Endpoints](#sales-service-endpoints)
      - [Reviews Service Endpoints](#reviews-service-endpoints)
  - [Testing](#testing)
  - [Documentation](#documentation)
  - [Contributing](#contributing)
  - [License](#license)

---

## Introduction

This project is a backend implementation of an e-commerce platform, focusing on the core functionalities required to manage customers, inventory, sales, and reviews. It is designed using microservices architecture to promote scalability, maintainability, and ease of development.

Each service is independently developed, tested, and deployed, allowing for flexible scaling and management.

---

## Project Overview

The e-commerce backend provides APIs for:

- **Customer Management**: Registration, login, profile updates, and wallet management.
- **Inventory Management**: Adding, updating, deleting, and viewing products.
- **Sales Management**: Processing purchases, updating inventory, and managing purchase history.
- **Review Management**: Submitting, approving, and viewing product reviews.

---

## Features

- **Microservices Architecture**: Independent services for customers, inventory, sales, and reviews.
- **RESTful APIs**: Standardized API endpoints for interaction with each service.
- **JWT Authentication**: Secure authentication using JSON Web Tokens.
- **Database Integration**: Persistent data storage using MySQL.
- **Containerization**: Dockerized services for consistent deployment.
- **Service Discovery**: Services communicate using DNS provided by Docker Compose.
- **Error Handling**: Robust error handling and validation.
- **Testing**: Unit and integration tests using Pytest.
- **Documentation**: Code documentation and API documentation using Sphinx.
- **Caching (Optional)**: Redis integration for caching frequently accessed data.

---

## Architecture

The application consists of four main services communicating over a Docker network:

- **Customers Service** (`localhost:8001`)
- **Inventory Service** (`localhost:8002`)
- **Sales Service** (`localhost:8003`)
- **Reviews Service** (`localhost:8004`)

A MySQL database is used for persistent storage, and Redis is optionally used for caching.

---

## Technologies Used

- **Programming Language**: Python 3.8
- **Frameworks**:
  - Flask
  - Flask-RESTful
  - Flask-JWT-Extended
- **Database**:
  - MySQL
  - SQLAlchemy (ORM)
- **Caching** (Optional):
  - Redis
- **Containerization**:
  - Docker
  - Docker Compose
- **Testing**:
  - Pytest
- **Documentation**:
  - Sphinx
- **Other Libraries**:
  - Marshmallow (Serialization/Deserialization)
  - Requests (HTTP Requests)

---

## Microservices

### Customers Service

Manages customer-related operations such as registration, authentication, profile management, and wallet balance.

### Inventory Service

Handles goods management, allowing for adding, updating, deleting, and viewing products.

### Sales Service

Manages sales transactions, processing purchases, and maintaining purchase history.

### Reviews Service

Handles product reviews and ratings, including submission, approval, and retrieval.

---

## Installation and Setup

### Prerequisites

- **Docker**: Install Docker Engine.
- **Docker Compose**: Install Docker Compose.
- **Git**: Install Git to clone the repository.

### Clone the Repository

```bash
git clone https://github.com/yourusername/ecommerce_backend_project.git
cd ecommerce_backend_project
```

### Environment Variables

Create a `.env` file in the root directory with the following content:

```dotenv
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@host:port/database_name'
JWT_SECRET_KEY=your_jwt_secret_key
```

### Building and Running with Docker Compose

Build and start all services using Docker Compose:

```bash
docker-compose up --build
```

---

## Usage

### Accessing the Services

The services are accessible via the following URLs:

- **Customers Service**: `http://127.0.0.1:5001`
- **Inventory Service**: `http://127.0.0.1:5002`
- **Sales Service**: `http://127.0.0.1:5003`
- **Reviews Service**: `http://127.0.0.1:5004`
- **Wishlist**: `http://127.0.0.1:5005`

---

## Testing

Each service includes unit and integration tests using Pytest.

To run tests for a service:

1. Navigate to the service directory:

   ```bash
   cd customers_service  # or other services
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-flask
   ```

3. Run tests:

   ```bash
   pytest
   ```

---

## Documentation

API documentation and code documentation are generated using Sphinx.

---

## Contributing

Contributions are welcome! Please fork the repository, create a new branch, and submit a pull request.

---
