from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from api.routers import llm_rag, route_opt, llm_sf

# Setup FastAPI app
app = FastAPI(title="API Server", description="API Server", version="v1")

# Enable CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=False,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
@app.get("/")
async def get_index():
    return {"message": "Welcome to Tripee"}

# Additional routers here
app.include_router(llm_sf.router, prefix="/llm-sf")
app.include_router(route_opt.router, prefix="/route-opt")
app.include_router(llm_rag.router, prefix="/llm-rag")
