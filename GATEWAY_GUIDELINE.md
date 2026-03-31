# API Gateway Verification Guideline

Use this guide to verify that the `API Gateway` correctly routes requests to all microservices.

## 1. Start Services

Open terminals from project root and run:

### Terminal A: Gateway (Port 8000)
```powershell
cd gateway
..\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Terminal B-H: Start All Microservices
Run each in a separate terminal:

**User Service (Port 8001)**
```powershell
cd user-service
..\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001
```

**Product Service (Port 8002)**
```powershell
cd product-service
..\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8002
```

**Cart Service (Port 8003)**
```powershell
cd cart-service
..\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8003
```

**Order Service (Port 8004)**
```powershell
cd order-service
..\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8004
```

**Inventory Service (Port 8005)**
```powershell
cd inventory-service
..\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8005
```

**Payment Service (Port 8006)**
```powershell
cd payment-service
..\venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8006
```

## 2. Test Gateway Root

### 2.1 Check gateway is running
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/ -Method GET
```

Expected:
- HTTP `200`
- Response: `{"message":"API Gateway is running on Port 8000. All traffic goes through here."}`

## 3. Test Gateway Routing to All Services

### 3.1 Route to Users
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/users/api/users -Method GET
```

Expected:
- HTTP `200`
- Array of users

### 3.2 Route to Products
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/products/ -Method GET
```

Expected:
- HTTP `200`
- Object with products array

### 3.3 Route to Cart
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/cart/api/cart/1 -Method GET
```

Expected:
- HTTP `200`
- Array of cart items (may be empty)

### 3.4 Route to Orders
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/orders/api/orders -Method GET
```

Expected:
- HTTP `200`
- Array of orders (may be empty)

### 3.5 Route to Inventory
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/inventory/api/inventory -Method GET
```

Expected:
- HTTP `200`
- Array of inventory items

### 3.6 Route to Payments
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/payments/api/payments -Method GET
```

Expected:
- HTTP `200`
- Array of payments (may be empty)

## 4. Test Gateway with POST Requests

### 4.1 Create user via gateway
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/users/api/users -Method POST -ContentType "application/json" -Body '{"name":"Test User","email":"test@example.com","role":"customer"}'
```

Expected:
- HTTP `201`
- User object with id, name, email, role

### 4.2 Create order via gateway
```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/orders/api/orders -Method POST -ContentType "application/json" -Body '{"user_id":1,"product_id":"p-101","quantity":2}'
```

Expected:
- HTTP `201`
- Order object with id, user_id, product_id, quantity, status

## 5. Verify via Swagger UI

### 5.1 Open Gateway Swagger
- URL: `http://127.0.0.1:8000/docs`

### 5.2 Test dynamic routing
1. Expand `GET /{service_name}/{path}` section
2. Enter parameters:
   - `service_name`: users
   - `path`: api/users
3. Click **Execute**
4. Expected: 200 status with user array

### 5.3 Repeat for other services
- `service_name`: products, `path`: /
- `service_name`: cart, `path`: api/cart/1
- `service_name`: orders, `path`: api/orders
- `service_name`: inventory, `path`: api/inventory
- `service_name`: payments, `path`: api/payments

## 6. Automated Verification Script

Run the automated verification to test all services at once:

```powershell
powershell -ExecutionPolicy Bypass -File .\verify-microservices.ps1
```

Expected:
- All 13 tests return PASS (7 direct + 6 via gateway)
- Output table shows 200 status codes for all rows

## 7. What to Screenshot (Proof)

Capture these screenshots:

1. Gateway root success
- URL: `http://127.0.0.1:8000/`
- Status: 200

2. Gateway routing test examples
- `http://127.0.0.1:8000/users/api/users` (Status 200)
- `http://127.0.0.1:8000/products/` (Status 200)
- `http://127.0.0.1:8000/orders/api/orders` (Status 200)

3. Swagger UI test
- `http://127.0.0.1:8000/docs`
- Screenshot showing successful execute with 200 status

4. Automated verification script result
- Terminal output showing all PASS results

## 8. How Gateway Works

**Route Pattern:** `http://127.0.0.1:8000/{service_name}/{path}`

Example:
- `http://127.0.0.1:8000/users/api/users` → forwards to `http://localhost:8001/api/users`
- `http://127.0.0.1:8000/products/p-101` → forwards to `http://localhost:8002/p-101`
- `http://127.0.0.1:8000/cart/api/cart/1` → forwards to `http://localhost:8003/api/cart/1`

**Supported HTTP Methods:** GET, POST, PUT, DELETE

## 9. Common Errors and Fixes

1. `404 Service not found in Gateway`
- Service name is not in the gateway mapping (must be: users, products, cart, orders, inventory, or payments)

2. `503 Service is currently down`
- Microservice is not running on its expected port
- Start the required service in a new terminal

3. `422 Unprocessable Content`
- POST/PUT request missing required JSON body
- Include proper body with required fields

4. Connection refused
- Gateway or microservice is not running
- Check all terminals are running and services are started

5. Wrong port error
- Ensure each service runs on correct port (8001-8006)
- Gateway must run on port 8000