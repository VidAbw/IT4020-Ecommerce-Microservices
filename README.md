# Ecommerce Microservices Project

This repository contains a set of FastAPI-based microservices for an ecommerce platform. The services are designed to be run as independent processes and communicate via HTTP through an API Gateway.

## 🚀 Getting Started

### 1. Prerequisites
- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

### 2. Setup

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd IT4020-Ecommerce-Microservices
   ```

2. **Create a Virtual Environment:**
   It's highly recommended to use a virtual environment to keep your dependencies organized.
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate   # On Windows
   ```

3. **Install Dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

### 3. Running the Microservices

Each service is an independent FastAPI application. You can run them manually in separate terminal windows:

- **Gateway:** `cd gateway; uvicorn main:app --reload --port 8000`
- **Users:** `cd user-service; uvicorn main:app --reload --port 8001`
- **Products:** `cd product-service; uvicorn main:app --reload --port 8002`
- **Cart:** `cd cart-service; uvicorn main:app --reload --port 8003`
- **Orders:** `cd order-service; uvicorn main:app --reload --port 8004`
- **Inventory:** `cd inventory-service; uvicorn main:app --reload --port 8005`
- **Payments:** `cd payment-service; uvicorn main:app --reload --port 8006`

Or run the verification script to start and test all services:
```powershell
.\verify-microservices.ps1
```

### 4. API Documentation (Swagger)

Each service provides interactive documentation:

- **Gateway:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Users:** [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
- **Products:** [http://127.0.0.1:8002/docs](http://127.0.0.1:8002/docs)
- **Cart:** [http://127.0.0.1:8003/docs](http://127.0.0.1:8003/docs)

### 5. Viewing the Database

Each service directory contains its own SQLite database file (e.g., `products.db`, `users.db`). These files are created automatically when the service is first run.

To view the data in any service:
1. Navigate to the service folder (e.g., `cd product-service`).
2. Run the database viewer script:
   ```powershell
   
   ```

### 6. Project Structure

```text
IT4020-Ecommerce-Microservices/
├── gateway/            # API Gateway (Port 8000)
├── user-service/  python view_db_data.py     # User Management (Port 8001)
├── product-service/    # Product Catalog (Port 8002)
├── cart-service/       # Shopping Cart (Port 8003)
├── order-service/      # Order Processing (Port 8004)
├── inventory-service/  # Stock Management (Port 8005)
├── payment-service/    # Payment Processing (Port 8006)
├── requirements.txt    # Project dependencies
└── view_db_data.py     # Database viewer script (present in each service)
```
