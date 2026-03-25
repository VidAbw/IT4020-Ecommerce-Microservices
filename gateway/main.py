from fastapi import FastAPI, Request, HTTPException, Response
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

# --- CORE ROUTING LOGIC ---
async def forward_request(service_name: str, path: str, request: Request):
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found in Gateway")

    microservice_url = f"{SERVICES[service_name]}/{path}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=microservice_url,
                headers=dict(request.headers),
                content=await request.body()
            )
            return Response(
                content=response.content, 
                status_code=response.status_code, 
                media_type=response.headers.get("content-type", "application/json")
            )
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail=f"{service_name.capitalize()} Service is currently down.")

# --- DYNAMIC ROUTES FOR ALL SERVICES ---
@app.get("/{service_name}/{path:path}", summary="Route GET requests")
async def route_get(service_name: str, path: str, request: Request):
    return await forward_request(service_name, path, request)

@app.post("/{service_name}/{path:path}", summary="Route POST requests")
async def route_post(service_name: str, path: str, request: Request):
    return await forward_request(service_name, path, request)

@app.put("/{service_name}/{path:path}", summary="Route PUT requests")
async def route_put(service_name: str, path: str, request: Request):
    return await forward_request(service_name, path, request)

@app.delete("/{service_name}/{path:path}", summary="Route DELETE requests")
async def route_delete(service_name: str, path: str, request: Request):
    return await forward_request(service_name, path, request)