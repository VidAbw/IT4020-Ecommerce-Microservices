from fastapi import FastAPI, Request, HTTPException
import httpx

app = FastAPI(title="E-Commerce API Gateway", version="1.0")

# Native Ports for the Microservices
SERVICES = {
    "users": "http://localhost:8001",
    "products": "http://localhost:8002",
    "cart": "http://localhost:8003",
    "orders": "http://localhost:8004",
    "inventory": "http://localhost:8005",
    "payments": "http://localhost:8006",
}

@app.get("/")
def gateway_root():
    return {"message": "API Gateway is running on Port 8000. All traffic goes through here."}

@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def route_traffic(service_name: str, path: str, request: Request):
    """
    Intercepts incoming traffic and routes it to the correct microservice.
    Example: GET /users/1 -> Forwards to http://localhost:8001/1
    """
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found in Gateway")

    # Construct the URL for the underlying microservice
    microservice_url = f"{SERVICES[service_name]}/{path}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=microservice_url,
                headers=dict(request.headers),
                content=await request.body()
            )
            return response.json()
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail=f"{service_name.capitalize()} Service is currently down.")