# main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

services = [
    {"name": "user-service", "url": "http://user-service:8081/openapi.json"},
    {"name": "order-service", "url": "http://order-service:8082/openapi.json"},
    {"name": "product-service", "url": "http://product-service:8083/openapi.json"},
    {"name": "inventory-service", "url": "http://inventory-service:8084/openapi.json"},
    {"name": "notification-service",
        "url": "http://notification-service:8085/openapi.json"},
    {"name": "payment-service", "url": "http://payment-service:8086/openapi.json"}
]


@app.get("/merged/openapi.json")
async def get_combined_openapi():
    combined_spec = {"openapi": "3.0.0", "info": {
        "title": "Combined API", "version": "1.0.0"}, "paths": {}}

    async with httpx.AsyncClient() as client:
        for service in services:
            response = await client.get(service["url"])
            spec = response.json()
            combined_spec["paths"].update(spec.get("paths", {}))

    return JSONResponse(content=combined_spec)
