import httpx
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="API Gateway (Macroservice)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BACKEND_URL = "http://backend:8000"
AUDIT_URL = "http://audit:8002"

@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(request: Request, path: str):
    persona = request.headers.get("x-persona", "User")
    method = request.method
    
    # Enforce persona rules
    if persona == "Viewer" and method in ["POST", "PUT", "DELETE"]:
        raise HTTPException(status_code=403, detail="Viewer persona cannot modify data.")
    if persona == "User" and method == "DELETE":
        raise HTTPException(status_code=403, detail="User persona cannot delete data.")
    
    # Route logic (Strangler Fig)
    target_url = BACKEND_URL
    if path.startswith("api/audit"):
        target_url = AUDIT_URL
        
    url = f"{target_url}/{path}"
    if request.query_params:
        url += f"?{request.query_params}"
        
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None) # Remove host header to avoid conflicts
    # Remove content-length as httpx will recalculate it
    headers.pop("content-length", None)
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body
            )
            # Filter hop-by-hop headers
            excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
            resp_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded_headers}
            return Response(content=resp.content, status_code=resp.status_code, headers=resp_headers)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Bad Gateway: {exc}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
